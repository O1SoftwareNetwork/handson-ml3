#! /usr/bin/env SQLALCHEMY_WARN_20=1 python
# Copyright 2023 O1 Software Network. MIT licensed.


from pathlib import Path

import pandas as pd
import sqlalchemy as sa
import typer


class Etl:
    def __init__(self, db_file: Path) -> None:
        self.engine = sa.create_engine(f"sqlite:///{db_file}")

    def create_table(self, in_csv: Path) -> None:
        date_cols = ["pickup_datetime", "dropoff_datetime"]
        df = pd.read_csv(in_csv, parse_dates=date_cols)
        df = self._discard_unhelpful_columns(df)
        df["distance"] = 0.0

        one_second = "1s"  # trim meaningless milliseconds from observations
        for col in date_cols:
            df[col] = df[col].dt.round(one_second)

        with self.engine.begin() as sess:
            sess.execute(self.ddl)
        df.to_sql("taxi", self.engine, if_exists="append", index=False)

    def _discard_unhelpful_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.drop(columns=["vendor_id"])  # TPEP: Creative Mobile or Verifone
        df = df.drop(columns=["store_and_fwd_flag"])  # only Y when out-of-range
        return df

    ddl = sa.text(
        """
    CREATE TABLE taxi (
        id                 TEXT  PRIMARY KEY,
        pickup_datetime    DATETIME,
        dropoff_datetime   DATETIME,
        passenger_count    INTEGER,
        pickup_longitude   FLOAT,
        pickup_latitude    FLOAT,
        dropoff_longitude  FLOAT,
        dropoff_latitude   FLOAT,
        trip_duration      INTEGER,
        distance           FLOAT
    )
    """
    )


def main(in_csv: Path) -> None:
    Etl(in_csv.parent / "taxi.db").create_table(in_csv)


if __name__ == "__main__":
    typer.run(main)
