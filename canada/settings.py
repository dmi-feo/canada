import os

import attr

from canada.yt_wb_manager.constants import YTAuthMode


@attr.s
class CanadaSettings:
    YT_HOST: str = attr.ib()
    ROOT_COLLECTION_NODE_ID: str = attr.ib()
    YT_AUTH_MODE: YTAuthMode = attr.ib(default=YTAuthMode.disabled)
    CA_FILE: str | None = attr.ib(default=None)

    @classmethod
    def from_env(cls):
        return cls(
            YT_HOST=os.environ["YT_HOST"],
            ROOT_COLLECTION_NODE_ID=os.environ["ROOT_COLLECTION_NODE_ID"],
            YT_AUTH_MODE=YTAuthMode(os.environ.get("YT_AUTH_MODE", YTAuthMode.disabled.value)),
            CA_FILE=os.environ.get("CA_FILE"),
        )
