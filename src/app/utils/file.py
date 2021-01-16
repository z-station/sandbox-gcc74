import os
import uuid
from app.config import TMP_DIR


class CppFile:

    def __init__(self, code: str):
        self.filepath_cpp = os.path.join(TMP_DIR, f'{uuid.uuid4()}.cpp')
        self.filepath_out = os.path.join(TMP_DIR, f'{uuid.uuid4()}.out')
        with open(self.filepath_cpp, 'w') as file:
            file.write(code)
        with open(self.filepath_out, 'w') as file:
            pass

    def remove(self):
        try:
            os.remove(self.filepath_cpp)
            os.remove(self.filepath_out)
        except:
            pass