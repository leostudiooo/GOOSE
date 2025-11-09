from pathlib import Path
from typing import Generic, TypeVar

import yaml
from pydantic import ValidationError, BaseModel
from yaml import YAMLError

from src.infrastructure.exceptions import ModelStorageError, ModelValidationError

T = TypeVar("T", bound=BaseModel)


class YAMLModelStorage(Generic[T]):
    def __init__(self, file_dir: Path, model_class: type[T]):
        self._file_dir = file_dir
        self._model_class = model_class

    def load(self, name: str) -> T:
        file_path = self._file_dir / f"{name}.yaml"
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f.read())
                return self._model_class.model_validate(data)
            except YAMLError as e:
                msg = f"从 YAML 文件 '{file_path}' 中加载数据模型失败"
                raise ModelStorageError(file_path, msg) from e
            except ValidationError as e:
                raise ModelValidationError(f"文件 '{file_path}' 验证不通过", e) from e

    def save(self, name, model: T) -> None:
        file_path = self._file_dir / f"{name}.yaml"
        with open(file_path, "w", encoding="utf-8") as f:
            try:
                f.write(yaml.safe_dump(model.model_dump(), allow_unicode=True))
            except Exception as e:
                msg = f"保存数据模型到 '{file_path}' 失败"
                raise ModelStorageError(file_path, msg) from e

    def with_file_dir(self, file_dir: Path) -> "YAMLModelStorage[T]":
        return YAMLModelStorage(file_dir, self._model_class)
