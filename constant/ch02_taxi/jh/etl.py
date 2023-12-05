#! /usr/bin/env SQLALCHEMY_WARN_20=1 python
# Copyright 2023 O1 Software Network. MIT licensed.


import re
from pathlib import Path
from time import time

import pandas as pd
import sqlalchemy as sa
import typer
from geopy.distance import distance
from ruamel.yaml import YAML


def timed(func, reporting_threshold_sec=0.1):
    def wrapped(*args, **kwargs):
        t0 = time()
        ret = func(*args, **kwargs)
        if func.__name__ != "wrapped":
            elapsed = time() - t0
            if elapsed > reporting_threshold_sec:
                print(f"  Elapsed time of {elapsed:.3f} seconds for {func.__name__}")
        return ret

    return wrapped


class Etl:
    """Extract, transform, and load Kaggle taxi data into a SQLite trip table."""

    def __init__(self, db_file: Path, decorator=timed) -> None:
        self.engine = sa.create_engine(f"sqlite:///{db_file}")

        for method_name in dir(self) + dir(Etl):
            attr = getattr(self, method_name)
            if re.match(r"<class '(function|method)'>", str(type(attr))):
                wrapped = decorator(attr)
                setattr(self, method_name, wrapped)

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

        self._write_yaml(df)

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
    # Distance from pickup to Grand Central can help with removing outliers.
    grand_central_nyc = 40.752, -73.978

    @classmethod
    def _distance(cls, row) -> float:
        from_ = row.pickup_latitude, row.pickup_longitude
        to = row.dropoff_latitude, row.dropoff_longitude
        dist = distance(from_, to).m

        # A post-processing step will discard trips that start "too far away".
        if distance(from_, cls.grand_central_nyc).m > cls.SERVICE_RADIUS:
            dist = -dist
        return round(dist, 2)

    @classmethod
    def _find_distance(cls, df: pd.DataFrame) -> pd.DataFrame:
        df["distance"] = df.apply(lambda row: cls._distance(row), axis=1)
        return df

    # Discard distant locations, e.g. the Verifone / Automation Anywhere
    # meter service center in San Jose, CA, locations in the North Atlantic.
    # SERVICE_RADIUS = 60_000  # 37 miles
    SERVICE_RADIUS = 150_000  # 93 miles

    @classmethod
    def _discard_outlier_rows(cls, df: pd.DataFrame) -> pd.DataFrame:
        df = df[df.distance >= 0]

        FOUR_HOURS = 4 * 60 * 60  # Somewhat commonly we see 86400 second "trips".
        # Discard trips where cabbie forgot to turn off the meter.
        df = df[df.trip_duration < FOUR_HOURS]

        df = df[df.distance < cls.SERVICE_RADIUS]

        assert df.passenger_count.max() <= 9
        return df

    def _write_yaml(self, df: pd.DataFrame, out_file="taxi.yml") -> None:
        ul, lr = self._get_bbox(df)

        d = dict(
            db_file=self.engine.url.database,
            grand_central_nyc=self.grand_central_nyc,
            service_radius=self.SERVICE_RADIUS,
            trip_count=len(df),
            ul=ul,
            lr=lr,
        )
        yaml = YAML()
        yaml.dump(d, Path(out_file))

    @staticmethod
    def _get_bbox(
        df: pd.DataFrame, prec: int = 3  # decimal places of precision
    ) -> tuple[tuple[float, float], tuple[float, float]]:
        n_lat = round(max(df.pickup_latitude.max(), df.dropoff_latitude.max()), prec)
        s_lat = round(min(df.pickup_latitude.min(), df.dropoff_latitude.min()), prec)
        w_lng = round(min(df.pickup_longitude.min(), df.dropoff_longitude.min()), prec)
        e_lng = round(max(df.pickup_longitude.max(), df.dropoff_longitude.max()), prec)
        ul = tuple(map(float, (n_lat, w_lng)))
        lr = tuple(map(float, (s_lat, e_lng)))
        return ul, lr


def main(in_csv: Path) -> None:
    Etl(in_csv.parent / "taxi.db").create_table(in_csv)


if __name__ == "__main__":
    typer.run(main)
