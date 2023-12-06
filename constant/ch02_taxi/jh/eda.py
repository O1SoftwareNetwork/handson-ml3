#! /usr/bin/env streamlit run --server.runOnSave true
# Copyright 2023 O1 Software Network. MIT licensed.

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from beartype import beartype

from constant.ch02_taxi.jh.etl import COMPRESSED_DATASET, Etl


@beartype
def eda(df: pd.DataFrame, num_rows=100_000) -> None:
    etl = Etl(COMPRESSED_DATASET.parent / "taxi.db")
    df = etl.discard_outlier_rows(df)[:num_rows]
    show_trip_locations(df)


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


def main(in_file=COMPRESSED_DATASET) -> None:
    eda(pd.read_parquet(in_file))


if __name__ == "__main__":
    main()
