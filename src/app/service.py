import subprocess
from typing import Union, Optional, List

from app.utils import msg
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
    RunResult,
    CppFile
)
from app import config


class CppService:

    @staticmethod
    def _clear(text: str):

        """ Удаляет из строки лишние спец. символы,
            которые добавляет Ace-editor """

        if isinstance(text, str):
            return text.replace('\r', '').rstrip('\n')
        else:
            return text

    @staticmethod
    def _compile_code(code: str) -> CompileResult:

        """ Компилирует код и возвращает результат """

        file = CppFile(code)
        result = CompileResult(file=file)
        proc = subprocess.Popen(
            args=['g++-7', file.filepath_cpp, '-o', file.filepath_out],
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

    @staticmethod
    def _run_code(console_input: Optional[str], file: CppFile):

        """ Запускает скомпилирвованный файл,
            передает входные данные
            и возвращает результат работы программы """

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

    @staticmethod
    def _run_checker(checker_code: str, **checker_locals) -> Union[bool, None]:

        """ Запускает код чекера на наборе переменных checker_locals
            возвращает результат работы чекера """

        try:
            exec(checker_code, globals(), checker_locals)
        except:
            return None
        else:
            return checker_locals.get('result')

    def _run_test(
        self,
        test: RequestTestData,
        compile_result: CompileResult,
        checker_code: str
    ) -> ResponseTestData:

        """ Запускает тест в компиляторе,
            сверяет результат работы программы и значение из теста чекером,
            определяет пройден ли тест и возвращает результат """

        result = ResponseTestData(
            test_console_input=test['test_console_input'],
            test_console_output=test['test_console_output'],
            translator_console_output=None,
            translator_error_msg=None,
            ok=False
        )
        if compile_result.error_msg:
            result['translator_error_msg'] = compile_result.error_msg
        else:
            run_result = self._run_code(
                console_input=self._clear(test['test_console_input']),
                file=compile_result.file
            )
            result['translator_error_msg'] = run_result.error_msg
            result['translator_console_output'] = run_result.console_output
            if not run_result.error_msg:
                test_ok = self._run_checker(
                    checker_code=checker_code,
                    test_console_output=self._clear(test['test_console_output']),
                    translator_console_output=run_result.console_output
                )
                if test_ok is None:
                    result['translator_error_msg'] = msg.CHECKER_ERROR
                elif test_ok:
                    result['ok'] = True
        return result

    def debug(self, data: RequestDebugDict) -> ResponseDebugDict:

        """ Прогоняет код в компиляторе с наборов входных данных
            и возвращает результат """

        console_input: str = self._clear(data.get('translator_console_input'))
        code: str = self._clear(data['code'])
        result = ResponseDebugDict()
        compile_result = self._compile_code(code)
        if compile_result.error_msg:
            result['translator_error_msg'] = compile_result.error_msg
        else:
            run_result = self._run_code(
                console_input=console_input,
                file=compile_result.file
            )
            result['translator_error_msg'] = run_result.error_msg
            result['translator_console_output'] = run_result.console_output

        compile_result.file.remove()
        return result

    def testing(self, data: RequestTestingDict) -> ResponseTestingDict:

        """ Прогоняет код на серии тестов в компиляторе
            и возвращает результат """

        code: str = self._clear(data['code'])
        tests: List[RequestTestData] = data['tests_data']
        checker_code: str = data['checker_code']

        result = ResponseTestingDict(
            num=len(tests), num_ok=0,
            ok=False, tests_data=[]
        )
        compile_result = self._compile_code(code)

        for test in tests:
            response_test_data = self._run_test(
                test=test,
                compile_result=compile_result,
                checker_code=checker_code
            )
            if response_test_data['ok']:
                result['num_ok'] += 1
            result['tests_data'].append(response_test_data)

        result['ok'] = result['num'] == result['num_ok']
        compile_result.file.remove()
        return result
