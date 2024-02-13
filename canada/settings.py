import os

import attr


@attr.s
class CanadaSettings:
    YT_HOST: str = attr.ib()
    ROOT_COLLECTION_NODE_ID: str = attr.ib()

    @classmethod
    def from_env(cls):
        return cls(
            YT_HOST=os.environ["YT_HOST"],
            ROOT_COLLECTION_NODE_ID=os.environ["ROOT_COLLECTION_NODE_ID"],
        )
