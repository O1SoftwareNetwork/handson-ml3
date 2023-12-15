#! /usr/bin/env python
# Copyright 2023 O1 Software Network. MIT licensed.
"""Feature augmentation."""

import warnings

import numpy as np
import pandas as pd
from cartopy.geodesic import Geodesic

warnings.filterwarnings("ignore", message="Conversion of an array with ndim > 0")

wgs84: Geodesic = Geodesic()


def add_pickup_dow_hour(df: pd.DataFrame) -> pd.DataFrame:
    """Add day-of-week and hour-of-day features."""
    df.loc[:, ("dow",)] = df["pickup_datetime"].copy().dt.dayofweek  # Monday=0
    df.loc[:, ("hour",)] = df["pickup_datetime"].copy().dt.hour
    df.loc[:, ("elapsed",)] = (
        df.dropoff_datetime - df.pickup_datetime
    ).dt.total_seconds()
    return df


def _direction(row: pd.Series) -> float:
    """Return azimuth of a single trip."""
    begin = (row["pickup_latitude"], row["pickup_longitude"])
    end = (row["dropoff_latitude"], row["dropoff_longitude"])
    bearing, _ = azimuth(begin, end)
    return round(bearing)


def add_direction(df: pd.DataFrame) -> pd.DataFrame:
    df["direction"] = df.apply(lambda row: _direction(row), axis=1)
    return df


def azimuth(
    begin_lat_lng: tuple[float, float], end_lat_lng: tuple[float, float]
) -> tuple[float, float]:
    """Return the azimuth angle when heading from BEGIN to END, and also distance."""
    begin_lng_lat = np.array(list(reversed(begin_lat_lng)))
    end_lng_lat = np.array(list(reversed(end_lat_lng)))
    meters, degrees, _ = map(int, wgs84.inverse(begin_lng_lat, end_lng_lat)[0])
    return degrees, meters
