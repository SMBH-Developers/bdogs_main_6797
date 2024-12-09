from abc import ABC, abstractmethod
class BaseOperation(ABC):
    
    @abstractmethod
    async def __call__(self, *args, **kwargs):
        raise NotImplementedError


class OperationFactory:
    def __init__(self):
        self._operations: dict[str, tuple[type[BaseOperation], dict]] = {}
    
    def register(self, key: str, operation_class: type[BaseOperation], dependencies: dict) -> None:
        if not issubclass(operation_class, BaseOperation):
            raise ValueError(f"Operation {operation_class.__name__} must inherit from BaseOperation")
        self._operations[key] = (operation_class, dependencies)
    
    def __getitem__(self, key: str) -> BaseOperation:
        if key not in self._operations:
            raise KeyError(f"Operation {key} not registered")
        operation_class, dependencies = self._operations[key]
        return operation_class(**dependencies)