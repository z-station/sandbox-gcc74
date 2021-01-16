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
    console_input: str = clear(data.get('translator_console_input', ''))
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

#
# @app.route('/testing/', methods=['post'])
# def testing() -> ResponseTestingDict:
#
#     data: RequestTestingDict = request.json
#     checker_code: str = data['checker_code']
#     tests: List[RequestTestData] = data['tests_data']
#     code: str = clear(data['code'])
#     file = CppFile(code)
#
#     tests_data = []
#     num_ok = 0
#     args = ['c++', file.filepath_cpp, '-o', file.filepath_out],
#     ok = False
#     translator_console_output = ''
#     translator_error_msg = ''
#     proc = subprocess.Popen(
#         args=args,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#     )
#     try:
#         stdout, stderr = proc.communicate(
#             timeout=config.TIMEOUT
#         )
#     except subprocess.TimeoutExpired:
#         translator_error_msg = msg.TIMEOUT
#         proc.kill()
#     except Exception as e:
#         translator_error_msg = f'Неожиданное исключение: {e}'
#         proc.kill()
#     else:
#         for test in tests:
#             test_console_input = clear(test['test_console_input'])
#             test_console_output = clear(test['test_console_output'])
#
#             translator_console_output, translator_error_msg = process_translator_response(
#                     stdout=stdout,
#                     stderr=stderr
#                 )
#                 if not translator_error_msg:
#                     ok = run_checker(
#                         checker_code=checker_code,
#                         test_console_output=test_console_output,
#                         translator_console_output=translator_console_output
#                     )
#                     if ok is None:
#                         translator_error_msg = msg.CHECKER_ERROR
#                 if ok:
#                     num_ok += 1
#
#             tests_data.append(
#                 ResponseTestData(
#                     test_console_input=test_console_input,
#                     test_console_output=test_console_output,
#                     translator_console_output=translator_console_output,
#                     translator_error_msg=translator_error_msg,
#                     ok=ok
#                 )
#             )
#
#     file.remove()
#     num = len(tests)
#     return ResponseTestingDict(
#         num=num,
#         num_ok=num_ok,
#         ok=num == num_ok,
#         tests_data=tests_data
#     )
