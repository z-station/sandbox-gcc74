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
from app.entities.translator import (
    CompileResult,
    RunResult
)
from app.utils.file import CppFile
from app.utils.translator import (
    clear,
    run_checker,
    compile_code,
    run_code
)
from app import config
from app.utils import msg

app = Flask(__name__)
CORS(app, origins=config.CORS_DOMAINS)


@app.route('/debug/', methods=['post'])
def debug() -> ResponseDebugDict:

    data: RequestDebugDict = request.json
    console_input: str = clear(data.get('translator_console_input'))
    code: str = clear(data['code'])

    result = ResponseDebugDict()
    compile_result = compile_code(code)
    if compile_result.error_msg:
        result['translator_error_msg'] = compile_result.error_msg
    else:
        run_result = run_code(
            console_input=console_input,
            file=compile_result.file
        )
        result['translator_error_msg'] = run_result.error_msg
        result['translator_console_output'] = run_result.console_output

    compile_result.file.remove()
    return result


@app.route('/testing/', methods=['post'])
def testing() -> ResponseTestingDict:

    data: RequestTestingDict = request.json
    code: str = clear(data['code'])
    tests: List[RequestTestData] = data['tests_data']
    checker_code: str = data['checker_code']

    result = ResponseTestingDict(
        num=len(tests),
        num_ok=0,
        ok=False,
        tests_data=[]
    )
    compile_result = compile_code(code)
    if compile_result.error_msg:
        for test in tests:
            result['tests_data'].append(
                ResponseTestData(
                    test_console_input=test['test_console_input'],
                    test_console_output=test['test_console_output'],
                    translator_console_output=None,
                    translator_error_msg=compile_result.error_msg,
                    ok=False
                )
            )
    else:
        for test in tests:
            response_test_data = ResponseTestData(
                test_console_input=test['test_console_input'],
                test_console_output=test['test_console_output'],
                translator_console_output=None,
                translator_error_msg=None,
                ok=False
            )
            run_result = run_code(
                console_input=clear(test['test_console_input']),
                file=compile_result.file
            )
            response_test_data['translator_error_msg'] = run_result.error_msg
            response_test_data['translator_console_output'] = run_result.console_output
            if not run_result.error_msg:
                test_ok = run_checker(
                    checker_code=checker_code,
                    test_console_output=clear(test['test_console_output']),
                    translator_console_output=run_result.console_output
                )
                if test_ok is None:
                    response_test_data['translator_error_msg'] = msg.CHECKER_ERROR
                elif test_ok:
                    result['num_ok'] += 1
                    response_test_data['ok'] = True
            result['tests_data'].append(response_test_data)

    compile_result.file.remove()
    result['ok'] = result['num'] == result['num_ok']
    return result
