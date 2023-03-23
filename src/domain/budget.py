from src.domain.entity import Id


class Budget:
    def __init__(self, id_: Id, histories_ids: frozenset[Id]) -> None:
        self._id = id_
        self._histories_ids = histories_ids

    @property
    def id(self) -> Id:
        return self._id

    @property
    def histories_ids(self) -> frozenset[Id]:
        return self._histories_ids
