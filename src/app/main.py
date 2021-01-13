import subprocess
from typing import List
from flask import Flask, request
from flask_cors import CORS
from app.entities.request import (
    RequestDebugDict,
    RequestTestData,
    RequestTestingDict
)
from app.entities.response import (
    ResponseDebugDict,
    ResponseTestData,
    ResponseTestingDict
)
from app.utils.file import CppFile
from app.utils.translator import (
    process_translator_response,
    clear,
    run_checker
)
from app import config
from app.utils import msg

app = Flask(__name__)
CORS(app, origins=config.CORS_DOMAINS)


@app.route('/debug/', methods=['post'])
def debug() -> ResponseDebugDict:

    data: RequestDebugDict = request.json
    translator_console_input: str = clear(data.get('translator_console_input', ''))
    translator_console_output = ''
    code: str = clear(data['code'])
    file = CppFile(code)
    try:
        proc = subprocess.Popen(
            args=['c++', file.filepath_cpp, '-o', file.filepath_out],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = proc.communicate(
            input=translator_console_input.encode('utf-8'),
            timeout=config.TIMEOUT
        )
        proc.kill()
    except subprocess.TimeoutExpired:
        translator_error_msg = msg.TIMEOUT
    except Exception as e:
        translator_error_msg = f'Неожиданное исключение на этапе компиляции : {e}'
    else:
        translator_console_output, translator_error_msg = process_translator_response(
            stdout=stdout,
            stderr=stderr
        )

    # ----
    if not translator_error_msg:
        try:
            proc = subprocess.Popen(
                args=[file.filepath_out],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = proc.communicate(
                input=translator_console_input.encode('utf-8'),
                timeout=config.TIMEOUT
            )
            proc.kill()
        except subprocess.TimeoutExpired:
            translator_error_msg = msg.TIMEOUT
        except Exception as e:
            translator_error_msg = f'Неожиданное исключение: {e}'
        else:
            translator_console_output, translator_error_msg = process_translator_response(
                stdout=stdout,
                stderr=stderr
            )
        finally:
            file.remove()

    return ResponseDebugDict(
        translator_console_output=translator_console_output,
        translator_error_msg=translator_error_msg
    )


@app.route('/testing/', methods=['post'])
def testing() -> ResponseTestingDict:

    data: RequestTestingDict = request.json
    checker_code: str = data['checker_code']
    tests: List[RequestTestData] = data['tests_data']
    code: str = clear(data['code'])
    file = PyFile(code)

    tests_data = []
    num_ok = 0
    args = ['python', file.filepath]
    for test in tests:
        ok = False
        test_console_input = clear(test['test_console_input'])
        test_console_output = clear(test['test_console_output'])
        translator_console_output = ''
        try:
            proc = subprocess.Popen(
                args=args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = proc.communicate(
                input=test_console_input.encode('utf-8'),
                timeout=config.TIMEOUT
            )
            proc.kill()
        except subprocess.TimeoutExpired:
            translator_error_msg = msg.TIMEOUT
        except Exception as e:
            translator_error_msg = f'Неожиданное исключение: {e}'
        else:
            translator_console_output, translator_error_msg = process_translator_response(
                stdout=stdout,
                stderr=stderr
            )
            if not translator_error_msg:
                ok = run_checker(
                    checker_code=checker_code,
                    test_console_output=test_console_output,
                    translator_console_output=translator_console_output
                )
                if ok is None:
                    translator_error_msg = msg.CHECKER_ERROR
            if ok:
                num_ok += 1

        tests_data.append(
            ResponseTestData(
                test_console_input=test_console_input,
                test_console_output=test_console_output,
                translator_console_output=translator_console_output,
                translator_error_msg=translator_error_msg,
                ok=ok
            )
        )

    file.remove()
    num = len(tests)
    return ResponseTestingDict(
        num=num,
        num_ok=num_ok,
        ok=num == num_ok,
        tests_data=tests_data
    )
