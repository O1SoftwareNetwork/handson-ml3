#! /usr/bin/env python
# Copyright 2023 O1 Software Network. MIT licensed.


import unittest

from constant.ch02_taxi.jh.features import azimuth

# This is very near both the median pickup and median dropoff point,
# Bryant Park behind the lions at the NYPL.
# Distance from pickup to Grand Central can help with removing outliers.
grand_central_nyc = 40.752, -73.978


class FeaturesTest(unittest.TestCase):
    logan_boston = 42.363, -71.006

    def test_azimuth(self) -> None:
        angle, distance = map(int, azimuth(grand_central_nyc, self.logan_boston))
        self.assertEqual((53, 305_719), (angle, distance))
