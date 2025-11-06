from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class ModelStorage(ABC, Generic[T]):
    """
    模型存储抽象基类
    
    定义了模型数据持久化的通用接口，支持加载和保存Pydantic模型。
    具体的存储格式（如YAML、JSON）由子类实现。
    """
    
    def __init__(self, file_path: Path, model_class: type[T]):
        """
        初始化模型存储
        
        Args:
            file_path: 存储文件路径
            model_class: Pydantic模型类
        """
        self.path = file_path
        self.model_class = model_class

    @abstractmethod
    def load(self) -> T:
        """
        从文件加载模型
        
        Returns:
            模型实例
            
        Raises:
            FileHandlerError: 当文件无法读取时
            ModelValidationError: 当数据验证失败时
        """
        ...

    @abstractmethod
    def save(self, model: T) -> None:
        """
        将模型保存到文件
        
        Args:
            model: 要保存的模型实例
            
        Raises:
            FileHandlerError: 当文件无法写入时
        """
        ...
