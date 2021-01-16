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
from app.utils.translator import (
    clear,
    compile_code,
    run_code,
    run_test,
    get_error_test_data
)
from app import config

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
        result['tests_data'] = get_error_test_data(
            tests=tests,
            error_msg=compile_result.error_msg
        )
    else:
        for test in tests:
            response_test_data = run_test(
                test=test,
                file=compile_result.file,
                checker_code=checker_code
            )
            result['tests_data'].append(response_test_data)
            if response_test_data['ok']:
                result['num_ok'] += 1

    compile_result.file.remove()
    result['ok'] = result['num'] == result['num_ok']
    return result
