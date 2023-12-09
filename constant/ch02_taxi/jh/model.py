#! /usr/bin/env python
# Copyright 2023 O1 Software Network. MIT licensed.
from pathlib import Path

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression

from constant.ch02_taxi.jh.etl import COMPRESSED_DATASET, discard_outlier_rows
from constant.ch02_taxi.jh.features import add_pickup_dow_hour
from constant.util.path import temp_dir


def linear_model() -> None:
    in_file: Path = COMPRESSED_DATASET
    df = pd.read_parquet(in_file)
    df = discard_outlier_rows(df)
    df = add_pickup_dow_hour(df)

    model = LinearRegression()
    model.fit(np.array(df.distance).reshape(-1, 1), df.elapsed)
    print(f"model.coef_: {model.coef_}")
    print(f"model.intercept_: {model.intercept_}")
    print(f"model.score(): {model.score(df[['distance']], df['elapsed'])}")
    sns.scatterplot(
        data=df,
        x="distance",
        y="elapsed",
    )
    # now plot the regression line
    xs = np.linspace(0, 40_000, 100)
    ys = model.predict(pd.DataFrame(xs))
    plt.plot(xs, ys, color="red")
    plt.title("Taxi Ride  Distance (m) vs. Elapsed time (s)")
    plt.savefig(temp_dir() / "constant/distance_vs_duration.png")
    plt.show()


if __name__ == "__main__":
    linear_model()
