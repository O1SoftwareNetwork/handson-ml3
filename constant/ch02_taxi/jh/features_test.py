#! /usr/bin/env python
# Copyright 2023 O1 Software Network. MIT licensed.

import unittest

import pandas as pd

from constant.ch02_taxi.jh.features import (
    add_direction,
    add_pickup_dow_hour,
    azimuth,
    grand_central_nyc,
)


class FeaturesTest(unittest.TestCase):
    logan_boston = 42.363, -71.006

    def setUp(self) -> None:
        df = pd.DataFrame(
            {
                "pickup_datetime": ["2019-01-01 12:00:00"],
                "dropoff_datetime": ["2019-01-01 16:00:00"],
                "pickup_latitude": [grand_central_nyc[0]],
                "pickup_longitude": [grand_central_nyc[1]],
                "dropoff_latitude": [self.logan_boston[0]],
                "dropoff_longitude": [self.logan_boston[1]],
            }
        )
        df['pickup_datetime'] = pd.to_datetime(df.pickup_datetime)
        df['dropoff_datetime'] = pd.to_datetime(df.dropoff_datetime)

        self.df = df

    def test_azimuth(self) -> None:
        angle, distance = map(int, azimuth(grand_central_nyc, self.logan_boston))
        self.assertEqual((53, 305_719), (angle, distance))

    def test_add_pickup_dow_hour(self) -> None:
        df = add_pickup_dow_hour(self.df)
        df = add_direction(df)
        self.assertEqual(1, df.dow[0])
        self.assertEqual(12, df.hour[0])
        self.assertEqual(4 * 3600, df.elapsed[0])
