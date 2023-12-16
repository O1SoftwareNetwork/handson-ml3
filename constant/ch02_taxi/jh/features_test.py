#! /usr/bin/env python
# Copyright 2023 O1 Software Network. MIT licensed.

import unittest

import pandas as pd

from constant.ch02_taxi.jh.features import (
    COMPRESSED_DATASET,
    add_direction,
    add_pickup_dow_hour,
    add_tlc_zone,
    azimuth,
    grand_central_nyc,
)
from constant.util.path import constant


class FeaturesTest(unittest.TestCase):
    logan_boston = 42.363, -71.006

    def setUp(self) -> None:
        self.df = pd.DataFrame(
            {
                "pickup_datetime": pd.to_datetime(["2019-01-01 12:00:00"]),
                "dropoff_datetime": pd.to_datetime(["2019-01-01 16:00:00"]),
                "pickup_latitude": [grand_central_nyc[0]],
                "pickup_longitude": [grand_central_nyc[1]],
                "dropoff_latitude": [self.logan_boston[0]],
                "dropoff_longitude": [self.logan_boston[1]],
            }
        )

    def test_azimuth(self) -> None:
        angle, distance = map(int, azimuth(grand_central_nyc, self.logan_boston))
        self.assertEqual((53, 305_719), (angle, distance))

    def test_add_pickup_dow_hour(self) -> None:
        df = add_pickup_dow_hour(self.df)
        df = add_direction(df)
        self.assertEqual(1, df.dow[0])
        self.assertEqual(12, df.hour[0])
        self.assertEqual(4 * 3600, df.elapsed[0])

    def test_constant(self) -> None:
        self.assertEqual('constant', constant().name)

    def test_tlc_zones(self) -> None:
        df = add_tlc_zone(self.df)
        self.assertEqual("Staten Island", ", ".join(df.borough.unique()))

        num_rows = 1_000
        df = pd.read_parquet(COMPRESSED_DATASET)[:num_rows]
        df = add_tlc_zone(df)
        # print(df.borough)
        # print(df.borough.unique())
        self.assertEqual("Staten Island", ", ".join(df.borough.unique()))
        # breakpoint()
