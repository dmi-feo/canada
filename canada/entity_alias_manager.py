from __future__ import annotations

import abc
import json
import os

import attr


class BaseEntityAliasManager(abc.ABC):
    @abc.abstractmethod
    def resolve_alias(self, alias: str) -> str:
        pass


class DummyEntityAliasManager(BaseEntityAliasManager):
    def resolve_alias(self, alias: str) -> str:
        return alias


@attr.s
class InMemoryEntityAliasManager(BaseEntityAliasManager):
    alias_to_id_map: dict[str, str] = attr.ib()

    @classmethod
    def from_file(cls, file_path: str) -> InMemoryEntityAliasManager:
        with open(file_path) as config_file:
            alias_to_id_map = json.load(config_file)["alias_to_id_map"]
        return cls(alias_to_id_map=alias_to_id_map)

    @classmethod
    def from_env(cls, env_var: str = "ALIAS_TO_ID_MAP") -> InMemoryEntityAliasManager:
        alias_to_id_map = json.loads(os.environ[env_var])
        return cls(alias_to_id_map=alias_to_id_map)

    def resolve_alias(self, alias: str) -> str:
        return self.alias_to_id_map.get(alias, alias)
