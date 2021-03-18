from abc import ABCMeta, abstractmethod


class Secret(metaclass=ABCMeta):
    def __init__(self, filename):
        self.data = None
        self.format = None
        self.load(filename)

    @abstractmethod
    def load(self, filename):
        pass

    @abstractmethod
    def save(self, filename):
        pass

    @abstractmethod
    def embed(self, secret: bytes):
        pass

    @abstractmethod
    def extract(self) -> bytes:
        pass
