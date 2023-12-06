#! /usr/bin/env python
# Copyright 2023 O1 Software Network. MIT licensed.
"""Feature augmentation."""


def add_pickup_dow_hour(df):
    """Add day-of-week and hour-of-day features."""
    df["dow"] = df["pickup_datetime"].dt.dayofweek  # Monday=0, Sunday=6
    df["hour"] = df["pickup_datetime"].dt.hour
    print(df.dow.describe())
    print(df.hour.describe())
    return df
