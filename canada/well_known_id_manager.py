from __future__ import annotations

import abc
import json

import attr


class BaseWellKnownIDManager(abc.ABC):
    @abc.abstractmethod
    def resolve_id(self, entity_id: str) -> str:
        pass


class DummyWellKnownIDManager(BaseWellKnownIDManager):
    def resolve_id(self, entity_id: str) -> str:
        return entity_id


@attr.s
class InMemoryWellKnownIDManager(BaseWellKnownIDManager):
    id_map: dict[str, str] = attr.ib()

    @classmethod
    def from_file(cls, file_path: str) -> InMemoryWellKnownIDManager:
        with open(file_path) as config_file:
            id_map = json.load(config_file)["id_map"]
        return cls(id_map=id_map)

    def resolve_id(self, entity_id: str) -> str:
        return self.id_map.get(entity_id, entity_id)
