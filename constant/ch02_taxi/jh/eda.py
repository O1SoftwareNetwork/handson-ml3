#! /usr/bin/env python
# Copyright 2023 O1 Software Network. MIT licensed.


import pandas as pd
from beartype import beartype

from constant.ch02_taxi.jh.etl import COMPRESSED_DATASET


@beartype
def eda(df: pd.DataFrame) -> None:
    print(df)


def main(in_file=COMPRESSED_DATASET) -> None:
    eda(pd.read_parquet(in_file))


if __name__ == "__main__":
    main()
