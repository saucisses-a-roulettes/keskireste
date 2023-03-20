import pickle
from src.application.history.repository import HistoryRepository
from src.domain.history import History


class HistoryPickleRepository(HistoryRepository):
    def retrieve(self, path: str) -> History:
        with open(path, "rb") as f:
            history: History = pickle.load(f)
        return history

    def save(self, history: History) -> None:
        with open(history.path, "wb") as f:
            pickle.dump(history, f)
