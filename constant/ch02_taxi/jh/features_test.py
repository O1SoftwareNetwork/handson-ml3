#! /usr/bin/env python
# Copyright 2023 O1 Software Network. MIT licensed.

import unittest

import duckdb
import pandas as pd

from constant.ch02_taxi.jh.features import (
    COMPRESSED_DATASET,
    add_direction,
    add_pickup_dow_hour,
    add_tlc_zone,
    azimuth,
    get_borough_matrix,
    grand_central_nyc,
)
from constant.util.path import constant
from constant.util.timing import timed


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
        self.assertEqual("constant", constant().name)

    @timed
    def test_read_prefix_rows_with_duckdb(self, n_rows=10) -> None:
        """Demonstrates how to rapidly read first few rows from parquet, ignoring the rest."""
        select = f'SELECT * FROM "{COMPRESSED_DATASET}" OFFSET {n_rows} LIMIT {n_rows}'
        df = duckdb.query(select).df()
        self.assertEqual(n_rows, len(df))

    def test_tlc_zones(self) -> None:
        df = add_tlc_zone(self.df)
        self.assertEqual("Manhattan", ", ".join(df.pickup_borough.unique()))

        base = 3_000  # The first few thousand rows omit the Bronx.
        num_rows = 1_000
        df = pd.read_parquet(COMPRESSED_DATASET)[base : base + num_rows]
        df = add_tlc_zone(df)

        boroughs = "Bronx, Brooklyn, EWR, Manhattan, Queens"  # Staten Island is rare.
        self.assertEqual(boroughs, ", ".join(sorted(df.pickup_borough.unique())))
        self.assertEqual(boroughs, ", ".join(sorted(df.dropoff_borough.unique())))

        #

        c = get_borough_matrix(df)
        self.assertEqual(5, len(c))
        self.assertEqual([928, 50, 20, 1, 1], sorted(c.values))

    # def test_get_borough_matrix(self) -> None:
