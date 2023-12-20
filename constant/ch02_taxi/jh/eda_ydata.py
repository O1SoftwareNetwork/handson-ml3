#! /usr/bin/env python
# Copyright 2023 O1 Software Network. MIT licensed.

from pathlib import Path

import pandas as pd
from ydata_profiling import ProfileReport

from constant.ch02_taxi.jh.features import COMPRESSED_DATASET


def main(in_file: Path = COMPRESSED_DATASET) -> None:
    df = pd.read_parquet(in_file)[:10_000]
    drops = [
        "pickup_datetime",
        "dropoff_datetime",
        #
        "pickup_longitude",
        "pickup_latitude",
        "dropoff_longitude",
        "dropoff_latitude",
    ]
    df = df.drop(columns=drops)
    print(df)
    ProfileReport(df).to_file("/tmp/k/trip.html")


if __name__ == "__main__":
    main()
