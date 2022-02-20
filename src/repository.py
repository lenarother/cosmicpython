from abc import ABC, abstractmethod

from src import model


class AbstractRepository(ABC):
    @abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abstractmethod
    def get(self, ref) -> model.Batch:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch):
        self.session.add(batch)

    def get(self, ref):
        return self.session.query(model.Batch).filter_by(ref=ref).one()  # noqa

    def list(self):
        return self.session.query(model.Batch).all()
