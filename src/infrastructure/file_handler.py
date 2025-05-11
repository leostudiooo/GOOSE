import logging
from pathlib import Path
from typing import Optional

from src.infrastructure.exceptions import FileHandlerError

logger = logging.getLogger(__name__)


class FileHandler:
    def __init__(
        self, file_path: Path, mode: str = "r", encoding: Optional[str] = "utf-8"
    ):
        self.file_path = file_path
        self.mode = mode
        self.encoding = encoding
        self.file = None

    def check_path(self):
        if not self.file_path.exists():
            msg = f"找不到名为 '{self.file_path}' 的文件"
            raise FileHandlerError(self.file_path, msg)

        if not self.file_path.is_file():
            msg = f"路径 '{self.file_path}' 不是一个常规文件"
            raise FileHandlerError(self.file_path, msg)

    def __enter__(self):
        self.check_path()
        try:
            self.file = open(self.file_path, self.mode, encoding=self.encoding)
            return self.file
        except Exception as e:
            raise FileHandlerError(self.file_path) from e

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file is None:
            return
        self.file.close()
