import os
import uuid
from app.config import TMP_DIR


class CppFile:

    def __init__(self, code: str):
        self.filepath_cpp = os.path.join(TMP_DIR, f'{uuid.uuid4()}.cpp')
        self.filepath_out = os.path.join(TMP_DIR, f'{uuid.uuid4()}.out')
        with open(self.filepath_cpp, 'w') as file:
            file.write(code)

    def remove(self):
        os.remove(self.filepath_cpp)
        os.remove(self.filepath_out)
