#! /usr/bin/env python
# Copyright 2023 O1 Software Network. MIT licensed.
"""Feature augmentation."""

import unittest
import warnings

import numpy as np
from cartopy.geodesic import Geodesic

from constant.ch02_taxi.jh.etl import grand_central_nyc

warnings.filterwarnings("ignore", message="Conversion of an array with ndim > 0")

wgs84 = Geodesic()


def add_pickup_dow_hour(df):
    """Add day-of-week and hour-of-day features."""
    df["dow"] = df["pickup_datetime"].dt.dayofweek  # Monday=0, Sunday=6
    df["hour"] = df["pickup_datetime"].dt.hour
    return df


def _direction(row):
    """Return azimuth of a single trip."""
    lat1, lon1, lat2, lon2 = row[
        ["pickup_latitude", "pickup_longitude", "dropoff_latitude", "dropoff_longitude"]
    ]
    return (lat2 - lat1, lon2 - lon1)


def add_direction(df):
    0


def azimuth(begin_lat_lng, end_lat_lng):
    """Return the azimuth angle when heading from BEGIN to END, and also distance."""
    begin_lng_lat = np.array(list(reversed(begin_lat_lng)))
    end_lng_lat = np.array(list(reversed(end_lat_lng)))
    meters, degrees, _ = map(int, wgs84.inverse(begin_lng_lat, end_lng_lat)[0])
    return degrees, meters


class FeaturesTest(unittest.TestCase):
    logan_boston = 42.363, -71.006

    def test_azimuth(self) -> None:
        angle, distance = map(int, azimuth(grand_central_nyc, self.logan_boston))
        self.assertEqual((53, 305_719), (angle, distance))
