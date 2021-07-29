import os
import uuid
import re
from abc import ABC
from typing import Optional
from dataclasses import dataclass

from app.utils import msg
from app.config import SANDBOX_DIR


class CppFile:

    """ Описывает файлы, необходимые для запуска программы """

    def __init__(self, code: str):
        self.filepath_cpp = os.path.join(SANDBOX_DIR, f'{uuid.uuid4()}.cpp')
        self.filepath_out = os.path.join(SANDBOX_DIR, f'{uuid.uuid4()}.out')
        with open(self.filepath_cpp, 'w') as file:
            file.write(code)
        with open(self.filepath_out, 'w') as _:
            pass

    def remove(self):
        try:
            os.remove(self.filepath_cpp)
            os.remove(self.filepath_out)
        except:
            pass


@dataclass
class BaseResult(ABC):

    _error_msg: Optional[str] = None

    @staticmethod
    def _remove_spec_chars(value: str) -> str:

        """ Удалить лишние спец-символы """

        return value.replace('\r', '').rstrip('\n')

    def _resolve_error_msg(self, value: str) -> str:

        """ Обработка текста сообщения об ошибке """

        error_msg = self._remove_spec_chars(
            value=re.sub(pattern='.*.[out|cpp]{1}:', repl="", string=value)
        )
        if 'Terminated' in error_msg:
            error_msg = msg.TIMEOUT
        elif 'Read-only file system' in error_msg:
            error_msg = msg.READ_ONLY_FS
        elif 'the monitored command dumped core' in error_msg:
            error_msg = msg.NEED_CONSOLE_INPUT
        return error_msg

    @property
    def error_msg(self):
        return self._error_msg

    @error_msg.setter
    def error_msg(self, value: Optional[str]):
        if value is not None:
            self._error_msg = self._resolve_error_msg(value)


@dataclass
class CompileResult(BaseResult):

    """ Описывает результат компиляции кода программы"""

    file: CppFile = None


@dataclass
class RunResult(BaseResult):

    """ Описывает результат запуска программы """

    _console_output: Optional[str] = None

    @property
    def console_output(self):
        return self._console_output

    @console_output.setter
    def console_output(self, value: Optional[str]):
        if value is not None:
            self._console_output = self._remove_spec_chars(value)
