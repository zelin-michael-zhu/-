from abc import ABC, abstractmethod


class BrowserExecutorBase(ABC):
    executor_type: str

    @abstractmethod
    def check_available(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    def open_url(self, session: str, url: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_state(self, session: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def click(self, session: str, target: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def fill(self, session: str, field: str, value: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def type_text(self, session: str, text: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def select(self, session: str, field: str, value: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def extract(self, session: str, instruction: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def screenshot(self, session: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def wait(self, session: str, condition: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def close(self, session: str) -> dict:
        raise NotImplementedError
