from pathlib import Path
from typing import Optional

from src.infrastructure.exceptions import FileHandlerError


class FileHandler:
    """
    文件处理上下文管理器
    
    提供安全的文件打开和关闭操作，自动进行路径验证和错误处理。
    可以使用with语句确保文件正确关闭。
    """
    
    def __init__(
        self, file_path: Path, mode: str = "r", encoding: Optional[str] = "utf-8"
    ):
        """
        初始化文件处理器
        
        Args:
            file_path: 文件路径
            mode: 文件打开模式（'r'=读取, 'w'=写入, 'rb'=二进制读取等）
            encoding: 文件编码，二进制模式时应设为None
        """
        self.path = file_path
        self.mode = mode
        self.encoding = encoding
        self.file = None

    def check_path(self) -> None:
        """
        验证文件路径
        
        检查文件是否存在（读取模式）以及路径是否为常规文件。
        
        Raises:
            FileHandlerError: 当文件不存在或路径不是常规文件时
        """
        if "r" in self.mode and not self.path.exists():
            msg = f"找不到名为 '{self.path}' 的文件"
            raise FileHandlerError(self.path, msg)

        if self.path.exists() and not self.path.is_file():
            msg = f"路径 '{self.path}' 不是一个常规文件"
            raise FileHandlerError(self.path, msg)

    def __enter__(self):
        """
        进入上下文管理器时打开文件
        
        Returns:
            打开的文件对象
            
        Raises:
            FileHandlerError: 当文件无法打开时
        """
        self.check_path()
        try:
            self.file = open(self.path, self.mode, encoding=self.encoding)
            return self.file
        except Exception as e:
            raise FileHandlerError(self.path) from e

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        退出上下文管理器时关闭文件
        
        Args:
            exc_type: 异常类型
            exc_val: 异常值
            exc_tb: 异常追踪信息
        """
        if self.file is None:
            return
        self.file.close()
