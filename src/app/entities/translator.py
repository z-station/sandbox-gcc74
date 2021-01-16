import re
from abc import ABC
from typing import Optional

from dataclasses import dataclass
from app.utils.file import CppFile
from app.utils import msg


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

    file: CppFile = None


@dataclass
class RunResult(BaseResult):

    _console_output: Optional[str] = None

    @property
    def console_output(self):
        return self._console_output

    @console_output.setter
    def console_output(self, value: Optional[str]):
        if value is not None:
            self._console_output = self._remove_spec_chars(value)
