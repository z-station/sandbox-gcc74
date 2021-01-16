import re
import subprocess
from typing import Tuple, Union

from app import config
from app.entities.translator import (
    RunResult, CompileResult
)
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


def run_code(console_input: str, file: CppFile):

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
