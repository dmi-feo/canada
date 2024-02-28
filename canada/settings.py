import os

import attr

from canada.yt_wb_manager.constants import YTAuthMode
from canada.constants import WellKnownIDMode


@attr.s
class CanadaSettings:
    YT_HOST: str = attr.ib()
    ROOT_COLLECTION_NODE_ID: str = attr.ib()
    YT_AUTH_MODE: YTAuthMode = attr.ib(default=YTAuthMode.disabled)
    CA_FILE: str | None = attr.ib(default=None)
    WELL_KNOWN_ID_MODE: WellKnownIDMode = attr.ib(default=WellKnownIDMode.disabled)
    WELL_KNOWN_ID_CONFIG_PATH: str | None = attr.ib(default=None)

    @classmethod
    def from_env(cls):
        return cls(
            YT_HOST=os.environ["YT_HOST"],
            ROOT_COLLECTION_NODE_ID=os.environ["ROOT_COLLECTION_NODE_ID"],
            YT_AUTH_MODE=YTAuthMode(os.environ.get("YT_AUTH_MODE", YTAuthMode.disabled.value)),
            CA_FILE=os.environ.get("CA_FILE"),
            WELL_KNOWN_ID_MODE=WellKnownIDMode(os.environ.get("WELL_KNOWN_ID_MODE", WellKnownIDMode.disabled.value)),
            WELL_KNOWN_ID_CONFIG_PATH=os.environ.get("WELL_KNOWN_ID_CONFIG_PATH"),
        )
