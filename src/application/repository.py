from src.domain.entity import Id


class CannotRetrieveEntity(Exception):
    def __init__(self, id_: Id) -> None:
        super().__init__(f"Cannot retrieve entity `{id_}`")
