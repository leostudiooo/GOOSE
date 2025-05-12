import json
from json import JSONDecodeError
from pathlib import Path
from typing import Generic

from pydantic import ValidationError

from src.infrastructure import FileHandler
from src.infrastructure.exceptions import FileHandlerError, ModelValidationError
from src.infrastructure.model_storage.model_storage import ModelStorage, T


class JSONModelStorage(ModelStorage, Generic[T]):
    def __init__(self, file_path: Path, model_class: type[T]):
        super().__init__(file_path, model_class)

    def load(self) -> T:
        with FileHandler(self.path) as f:
            try:
                return self.model_class.model_validate(json.loads(f.read()))
            except JSONDecodeError as e:
                msg = f"解析 JSON 文件 '{self.path}' 失败"
                raise FileHandlerError(self.path, msg) from e
            except ValidationError as e:
                raise ModelValidationError(f"文件 '{self.path}' 验证不通过", e) from e

    def save(self, model: T):
        with FileHandler(self.path, "w") as f:
            try:
                f.write(model.model_dump_json(indent=4))
            except Exception as e:
                msg = f"保存文件 '{self.path}' 失败"
                raise FileHandlerError(self.path, msg) from e
