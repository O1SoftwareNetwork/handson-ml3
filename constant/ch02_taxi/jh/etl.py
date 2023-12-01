#! /usr/bin/env SQLALCHEMY_WARN_20=1 python
# Copyright 2023 O1 Software Network. MIT licensed.


from pathlib import Path

import geopy.distance
import pandas as pd
import sqlalchemy as sa
import typer
from ruamel.yaml import YAML


class Etl:
    """Extract, transform, and load Kaggle taxi data into a SQLite trip table."""

    def __init__(self, db_file: Path) -> None:
        self.engine = sa.create_engine(f"sqlite:///{db_file}")

    def create_table(self, in_csv: Path) -> None:
        date_cols = ["pickup_datetime", "dropoff_datetime"]
        df = pd.read_csv(in_csv, parse_dates=date_cols)
        df = self._discard_unhelpful_columns(df)
        df["distance"] = 0.0
        self._find_distance(df)  # This costs 6 minutes for 1.46 M rows (4200 row/sec)
        self._discard_outlier_rows(df)

        one_second = "1s"  # trim meaningless milliseconds from observations
        for col in date_cols:
            df[col] = df[col].dt.round(one_second)

        with self.engine.begin() as sess:
            sess.execute(sa.text("DROP TABLE  IF EXISTS  trip"))
            sess.execute(self.ddl)
        df.to_sql("trip", self.engine, if_exists="append", index=False)

        self._write_yaml()

    @staticmethod
    def _discard_unhelpful_columns(df: pd.DataFrame) -> pd.DataFrame:
        df = df.drop(columns=["vendor_id"])  # TPEP: Creative Mobile or Verifone
        df = df.drop(columns=["store_and_fwd_flag"])  # only Y when out-of-range
        return df

    ddl = sa.text(
        """
    CREATE TABLE trip (
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

    # This is very near both the median pickup and median dropoff point,
    # Bryant Park behind the lions at the NYPL.
    grand_central_nyc = 40.752, -73.978

    @staticmethod
    def _distance(row, center) -> float:
        return round(
            geopy.distance.distance(
                (row.dropoff_latitude, row.dropoff_longitude), center
            ).m,
            2,
        )

    @classmethod
    def _find_distance(cls, df: pd.DataFrame) -> pd.DataFrame:
        center = cls.grand_central_nyc
        df["distance"] = df.apply(lambda row: cls._distance(row, center), axis=1)
        return df

    @staticmethod
    def _discard_outlier_rows(df: pd.DataFrame) -> pd.DataFrame:
        FOUR_HOURS = 4 * 60 * 60  # Somewhat commonly we see 86400 second "trips".
        # Discard trips where cabbie forgot to turn off the meter.
        df = df[df.trip_duration < FOUR_HOURS]

        # Discard distant locations, e.g. the Verifone / Automation Anywhere
        # meter service center in San Jose, CA, locations in the North Atlantic.
        # SERVICE_RADIUS = 60_000  # 37 miles
        SERVICE_RADIUS = 140_000  # 87 miles
        df = df[df.distance < SERVICE_RADIUS]

        assert df.passenger_count.max() <= 9
        return df

    def _write_yaml(self, out_file="taxi.yml") -> None:
        d = dict(
            db_file=self.engine.url.database,
            grand_central_nyc=self.grand_central_nyc,
        )
        yaml = YAML()
        yaml.dump(d, Path(out_file))


def main(in_csv: Path) -> None:
    Etl(in_csv.parent / "taxi.db").create_table(in_csv)


if __name__ == "__main__":
    typer.run(main)
