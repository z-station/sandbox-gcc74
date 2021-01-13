import re
from typing import Tuple, Union
from app.utils import msg


def clear(text: str):

    """ Удаляет из строки лишние спец. символы,
        которые добавляет Ace-editor """

    if isinstance(text, str):
        return text.replace('\r', '').rstrip('\n')
    else:
        return text


def process_translator_error(stderr: bytes) -> str:

    """ Обработка текста сообщения об ошибке """

    result = clear(
        re.sub(pattern='.*.[out|cpp]{1}:', repl="", string=stderr.decode())
    )
    if 'Terminated' in result:
        return msg.TIMEOUT
    elif 'Read-only file system' in result:
        return msg.READ_ONLY_FS
    elif 'the monitored command dumped core' in result:
        return msg.NEED_CONSOLE_INPUT
    else:
        return result


def process_translator_response(stdout: bytes, stderr: bytes) -> Tuple[str, str]:

    """ Преобразует bytes (вывод интерпретатора) в unicode, удаляет лишние символы из вывода """

    output = '' if stdout is None else stdout.decode()
    error = '' if stderr is None else process_translator_error(stderr)
    return output, error


def run_checker(checker_code: str, **checker_locals) -> Union[bool, None]:

    """ Запускает код чекера на наборе переменных checker_locals
        возвращает результат работы чекера """

    try:
        exec(checker_code, globals(), checker_locals)
    except:
        return None
    else:
        return checker_locals.get('result')
