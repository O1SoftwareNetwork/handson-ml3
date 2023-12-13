#! /usr/bin/env python
# Copyright 2023 O1 Software Network. MIT licensed.

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from beartype import beartype

from constant.ch02_taxi.jh.etl import COMPRESSED_DATASET, discard_outlier_rows
from constant.ch02_taxi.jh.features import add_pickup_dow_hour


@beartype
def eda_distance(df: pd.DataFrame, num_rows: int = 100_000) -> None:
    df = discard_outlier_rows(df)[:num_rows]
    df = add_pickup_dow_hour(df)
    show_distance_vs_time(df)


@beartype
def show_distance_vs_time(df: pd.DataFrame) -> None:
    fig, _ = plt.subplots()
    assert fig
    sns.scatterplot(
        data=df,
        x="distance",
        y="elapsed",
    )
    plt.show()


@beartype
def eda_min_time(df: pd.DataFrame) -> None:
    df["distance_km"] = (df.distance / 1000).apply(int)
    min_time = df.groupby("distance_km").elapsed.min().reset_index()
    show_min_time(min_time)


@beartype
def show_min_time(df: pd.DataFrame) -> None:
    # 13.3 m/s is 30 mph
    sns.regplot(
        data=df,
        x="distance_km",
        y="elapsed",
    )
    plt.show()


@beartype
def main(in_file: Path = COMPRESSED_DATASET, num_rows: int = 100_000) -> None:
    df = pd.read_parquet(in_file)[:num_rows]
    df = discard_outlier_rows(df)
    df = add_pickup_dow_hour(df)

    eda_min_time(df)
    # eda_distance(pd.read_parquet(in_file))


if __name__ == "__main__":
    main()
