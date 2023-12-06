#! /usr/bin/env streamlit run --server.runOnSave true
# Copyright 2023 O1 Software Network. MIT licensed.

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
from beartype import beartype

from constant.ch02_taxi.jh.etl import COMPRESSED_DATASET
from constant.ch02_taxi.jh.features import add_pickup_dow_hour


def eda_time(df: pd.DataFrame, num_rows: int = 100_000) -> None:
    df = add_pickup_dow_hour(df[:num_rows])
    show_dropoff_locations(df)


def show_dropoff_locations(df: pd.DataFrame) -> None:
    fig, _ = plt.subplots()
    sns.scatterplot(
        data=df,
        x="dropoff_longitude",
        y="dropoff_latitude",
        size=2,
        alpha=0.02,
        color="purple",
    )
    st.write(fig)


@beartype
def main(in_file: Path = COMPRESSED_DATASET) -> None:
    eda_time(pd.read_parquet(in_file))


if __name__ == "__main__":
    main()
