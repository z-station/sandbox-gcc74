import subprocess
from typing import Union, Optional, List

from app import config
from app.entities.translator import (
    RunResult, CompileResult
)
from app.entities.request import RequestTestData
from app.entities.response import ResponseTestData
from app.utils import msg
from app.utils.file import CppFile


def clear(text: str):

    """ Удаляет из строки лишние спец. символы,
        которые добавляет Ace-editor """

    if isinstance(text, str):
        return text.replace('\r', '').rstrip('\n')
    else:
        return text


def compile_code(code: str) -> CompileResult:

    """ Компилирует код и возвращает результат """

    file = CppFile(code)
    result = CompileResult(file=file)
    proc = subprocess.Popen(
        args=['c++', file.filepath_cpp, '-o', file.filepath_out],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    try:
        _, result.error_msg = proc.communicate(timeout=config.TIMEOUT)
    except subprocess.TimeoutExpired:
        result.error_msg = msg.TIMEOUT
        proc.kill()
    except Exception as e:
        result.error_msg = f'Неожиданное исключение на этапе компиляции : {e}'
        proc.kill()
    return result


def run_code(console_input: Optional[str], file: CppFile):

    """ Запускает скомпилирвованный файл и возвращает результат работы программы """

    result = RunResult()
    proc = subprocess.Popen(
        args=[file.filepath_out],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    try:
        result.console_output, result.error_msg = proc.communicate(
            input=console_input,
            timeout=config.TIMEOUT
        )
    except subprocess.TimeoutExpired:
        result.error_msg = msg.TIMEOUT
        proc.kill()
    except Exception as e:
        result.error_msg = f'Неожиданное исключение: {e}'
        proc.kill()
    return result


def run_checker(checker_code: str, **checker_locals) -> Union[bool, None]:

    """ Запускает код чекера на наборе переменных checker_locals
        возвращает результат работы чекера """

    try:
        exec(checker_code, globals(), checker_locals)
    except:
        return None
    else:
        return checker_locals.get('result')


def get_error_test_data(
    error_msg: str,
    tests: List[RequestTestData]
) -> List[ResponseTestData]:
    
    result = []
    for test in tests:
        result.append(
            ResponseTestData(
                test_console_input=test['test_console_input'],
                test_console_output=test['test_console_output'],
                translator_console_output=None,
                translator_error_msg=error_msg,
                ok=False
            )
        )
    return result


def run_test(
    test: RequestTestData,
    file: CppFile,
    checker_code: str
) -> ResponseTestData:

    result = ResponseTestData(
        test_console_input=test['test_console_input'],
        test_console_output=test['test_console_output'],
        translator_console_output=None,
        translator_error_msg=None,
        ok=False
    )
    run_result = run_code(
        console_input=clear(test['test_console_input']),
        file=file
    )
    result['translator_error_msg'] = run_result.error_msg
    result['translator_console_output'] = run_result.console_output
    if not run_result.error_msg:
        test_ok = run_checker(
            checker_code=checker_code,
            test_console_output=clear(test['test_console_output']),
            translator_console_output=run_result.console_output
        )
        if test_ok is None:
            result['translator_error_msg'] = msg.CHECKER_ERROR
        elif test_ok:
            result['ok'] = True

    return result
