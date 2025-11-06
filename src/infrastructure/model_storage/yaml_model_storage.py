from pathlib import Path
from typing import Generic

import yaml
from pydantic import ValidationError
from yaml import YAMLError

from src.infrastructure import FileHandler
from src.infrastructure.exceptions import FileHandlerError, ModelValidationError
from src.infrastructure.model_storage.model_storage import ModelStorage, T


class YAMLModelStorage(ModelStorage, Generic[T]):
    """
    YAML格式的模型存储实现
    
    使用YAML格式序列化和反序列化Pydantic模型。
    """
    
    def __init__(self, file_path: Path, model_class: type[T]):
        """
        初始化YAML模型存储
        
        Args:
            file_path: YAML文件路径
            model_class: Pydantic模型类
        """
        super().__init__(file_path, model_class)

    def load(self) -> T:
        """
        从YAML文件加载模型
        
        Returns:
            模型实例
            
        Raises:
            FileHandlerError: 当YAML文件无法解析时
            ModelValidationError: 当数据验证失败时
        """
        with FileHandler(self.path) as f:
            try:
                data = yaml.safe_load(f.read())
                return self.model_class.model_validate(data)
            except YAMLError as e:
                msg = f"解析 YAML 文件 '{self.path}' 失败"
                raise FileHandlerError(Path(self.path), msg) from e
            except ValidationError as e:
                raise ModelValidationError(f"文件 '{self.path}' 验证不通过", e) from e

    def save(self, model: T) -> None:
        """
        将模型保存为YAML文件
        
        Args:
            model: 要保存的模型实例
            
        Raises:
            FileHandlerError: 当文件无法写入时
        """
        with FileHandler(self.path, "w") as f:
            try:
                f.write(yaml.safe_dump(model.model_dump(), allow_unicode=True))
            except Exception as e:
                msg = f"保存文件 '{self.path}' 失败"
                raise FileHandlerError(Path(self.path), msg) from e