from pathlib import Path
from typing import Generic

import yaml
from pydantic import ValidationError
from yaml import YAMLError

from src.infrastructure import FileHandler
from src.infrastructure.exceptions import FileHandlerError, ModelValidationError
from src.infrastructure.model_storage.model_storage import ModelStorage, T


class YAMLModelStorage(ModelStorage, Generic[T]):
    def __init__(self, file_path: Path, model_class: type[T]):
        super().__init__(file_path, model_class)

    def load(self) -> T:
        with FileHandler(self.path) as f:
            try:
                data = yaml.safe_load(f.read())
                
                # 特殊处理 User 类的 custom_track 字段
                if self.model_class.__name__ == "User" and isinstance(data.get("custom_track"), str):
                    # 如果是非空字符串，转换为启用的对象格式
                    if data["custom_track"]:
                        data["custom_track"] = {
                            "enable": True,
                            "file": data["custom_track"]
                        }
                    # 如果是空字符串，转换为禁用的对象格式
                    else:
                        data["custom_track"] = {
                            "enable": False,
                            "file": ""
                        }
                    
                return self.model_class.model_validate(data)
            except YAMLError as e:
                msg = f"解析 YAML 文件 '{self.path}' 失败"
                raise FileHandlerError(Path(self.path), msg) from e
            except ValidationError as e:
                raise ModelValidationError(f"文件 '{self.path}' 验证不通过", e) from e

    def save(self, model: T) -> None:
        with FileHandler(self.path, "w") as f:
            try:
                f.write(yaml.safe_dump(model.model_dump(), allow_unicode=True))
            except Exception as e:
                msg = f"保存文件 '{self.path}' 失败"
                raise FileHandlerError(Path(self.path), msg) from e
