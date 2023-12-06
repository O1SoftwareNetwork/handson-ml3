#! /usr/bin/env python
# Copyright 2023 O1 Software Network. MIT licensed.

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from beartype import beartype

from constant.ch02_taxi.jh.etl import COMPRESSED_DATASET, Etl
from constant.ch02_taxi.jh.features import add_pickup_dow_hour


@beartype
def eda_map(df: pd.DataFrame, num_rows=100_000) -> None:
    etl = Etl(COMPRESSED_DATASET.parent / "taxi.db")
    df = etl.discard_outlier_rows(df)[:num_rows]
    df = add_pickup_dow_hour(df)
    show_trip_locations(df)


@beartype
def show_trip_locations(df: pd.DataFrame) -> None:
    fig, _ = plt.subplots()
    assert fig
    sns.scatterplot(
        data=df,
        # x="pickup_longitude",
        # y="pickup_latitude",
        x="dropoff_longitude",
        y="dropoff_latitude",
        size=2,
        alpha=0.02,
        color="purple",
    )
    plt.show()


@beartype
def main(in_file=COMPRESSED_DATASET) -> None:
    eda_map(pd.read_parquet(in_file))


if __name__ == "__main__":
    main()
