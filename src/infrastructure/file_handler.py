from pathlib import Path
from typing import Optional

from src.infrastructure.exceptions import FileHandlerError


class FileHandler:
    def __init__(
        self, file_path: Path, mode: str = "r", encoding: Optional[str] = "utf-8"
    ):
        self._path = file_path
        self._mode = mode
        self._encoding = encoding
        self._file = None

    def check_path(self):
        if "r" in self._mode and not self._path.exists():
            msg = f"找不到名为 '{self._path}' 的文件"
            raise FileHandlerError(self._path, msg)

        if self._path.exists() and not self._path.is_file():
            msg = f"路径 '{self._path}' 不是一个常规文件"
            raise FileHandlerError(self._path, msg)

    def __enter__(self):
        self.check_path()
        try:
            self._file = open(self._path, self._mode, encoding=self._encoding)
            return self._file
        except Exception as e:
            raise FileHandlerError(self._path) from e

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._file is None:
            return
        self._file.close()
