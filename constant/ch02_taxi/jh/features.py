#! /usr/bin/env python
# Copyright 2023 O1 Software Network. MIT licensed.
"""Feature augmentation."""

import warnings
from collections import namedtuple

import dbf
import geopandas as gpd
import numpy as np
import pandas as pd
from cartopy.geodesic import Geodesic

from constant.util.path import temp_dir

warnings.filterwarnings("ignore", message="Conversion of an array with ndim > 0")

wgs84: Geodesic = Geodesic()


# This is very near both the median pickup and median dropoff point,
# Bryant Park behind the lions at the NYPL.
# Distance from pickup to Grand Central can help with removing outliers.
grand_central_nyc = 40.752, -73.978


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


TLCZone = namedtuple("TLCZone", "locationid borough zone")


def _unused_get_tlc_names():
    # FieldnameList(['OBJECTID', 'SHAPE_LENG', 'SHAPE_AREA', 'ZONE', 'LOCATIONID', 'BOROUGH'])
    tbl = dbf.Table("/tmp/taxi_zones.dbf")
    assert 6 == tbl.field_count
    tbl.open()
    for row in tbl.query("SELECT *  ORDER BY locationid"):
        i = int(row.locationid)
        borough, zone = map(str.rstrip, (row.borough, row.zone))
        yield i, TLCZone(i, borough, zone)
    tbl.close()


_tlc_zone_shapes = gpd.read_file(temp_dir() / "taxi_zones.shp")
_tlc_zones = dict(_get_tlc_names())


def add_tlc_zone(df: pd.DataFrame) -> pd.DataFrame:
    df["pickup_pt"] = gpd.points_from_xy(df.pickup_longitude, df.pickup_latitude)
    df["dropoff_pt"] = gpd.points_from_xy(df.dropoff_longitude, df.dropoff_latitude)

    gdf = gpd.GeoDataFrame(df).set_geometry("pickup_pt")
    joined = gdf.sjoin_nearest(_tlc_zone_shapes, how="left")
    df["locationid"] = joined.LocationID
    df["zone"] = joined.zone
    print(df.zone)
    breakpoint()
    return df
