from pathlib import Path
from typing import Generic, TypeVar

import yaml
from pydantic import ValidationError, BaseModel
from yaml import YAMLError

from src.infrastructure import FileHandler
from src.infrastructure.exceptions import FileHandlerError, ModelValidationError

T = TypeVar("T", bound=BaseModel)

class YAMLModelStorage(Generic[T]):
    def __init__(self, file_dir: Path, model_class: type[T]):
        self._file_dir = file_dir
        self._model_class = model_class

    def load(self, name) -> T:
        file_path = self._file_dir / f"{name}.yaml"
        with FileHandler(file_path) as f:
            try:
                data = yaml.safe_load(f.read())
                return self._model_class.model_validate(data)
            except YAMLError as e:
                msg = f"解析 YAML 文件 '{file_path}' 失败"
                raise FileHandlerError(file_path, msg) from e
            except ValidationError as e:
                raise ModelValidationError(f"文件 '{file_path}' 验证不通过", e) from e

    def save(self, name, model: T) -> None:
        file_path = self._file_dir / f"{name}.yaml"
        with FileHandler(file_path, "w") as f:
            try:
                f.write(yaml.safe_dump(model.model_dump(), allow_unicode=True))
            except Exception as e:
                msg = f"保存文件 '{file_path}' 失败"
                raise FileHandlerError(file_path, msg) from e

    def set_file_dir(self, dir_path: Path) -> "YAMLModelStorage":
        self._file_dir = dir_path
        return self

    def get_file_dir(self) -> Path:
        return self._file_dir
