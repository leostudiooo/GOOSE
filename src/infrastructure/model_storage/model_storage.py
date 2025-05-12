from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class ModelStorage(ABC, Generic[T]):
    def __init__(self, file_path: Path, model_class: type[T]):
        self.path = file_path
        self.model_class = model_class

    @abstractmethod
    def load(self) -> T: ...

    @abstractmethod
    def save(self, model: T): ...
