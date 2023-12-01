#! /usr/bin/env SQLALCHEMY_WARN_20=1 python
# Copyright 2023 O1 Software Network. MIT licensed.


from pathlib import Path

import pandas as pd
import sqlalchemy as sa
from beartype import beartype


@beartype
class BBox:
    """Report on trip table bounding boxes. How far do taxis roam?"""

    def __init__(self, db_file: Path) -> None:
        self.engine = sa.create_engine(f"sqlite:///{db_file}")

    def report(self) -> None:
        0


def main(db_file="/tmp/constant/taxi.db") -> None:
    BBox(Path(db_file)).report()


if __name__ == "__main__":
    main()
