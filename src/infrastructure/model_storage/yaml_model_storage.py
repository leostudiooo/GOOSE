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
                return self.model_class.model_validate(yaml.safe_load(f.read()))
            except YAMLError as e:
                msg = f"解析 YAML 文件 '{self.path}' 失败"
                raise FileHandlerError(Path(self.path), msg) from e
            except ValidationError as e:
                raise ModelValidationError(f"文件 '{self.path}' 验证不通过", e) from e

    def save(self, model: T) -> None:
        with FileHandler(self.path, "w") as f:
            try:
                f.write(yaml.safe_dump(model.model_dump()))
            except Exception as e:
                msg = f"保存文件 '{self.path}' 失败"
                raise FileHandlerError(Path(self.path), msg) from e
