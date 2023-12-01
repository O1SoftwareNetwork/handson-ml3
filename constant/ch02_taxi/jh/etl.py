#! /usr/bin/env python
# Copyright 2023 O1 Software Network. MIT licensed.


from pathlib import Path

import pandas as pd
import typer


def create_table(in_csv: Path) -> None:
    date_cols = ["pickup_datetime", "dropoff_datetime"]
    df = pd.read_csv(in_csv, parse_dates=date_cols)
    df = _discard_unhelpful_columns(df)

    one_second = "1s"  # trim meaningless milliseconds from observations
    for col in date_cols:
        df[col] = df[col].dt.round(one_second)

    print(df)


def _discard_unhelpful_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop(columns=["vendor_id"])  # TPEP: Creative Mobile or Verifone
    df = df.drop(columns=["store_and_fwd_flag"])  # only Y when out- {of-town, of-range}
    return df


if __name__ == "__main__":
    typer.run(create_table)
