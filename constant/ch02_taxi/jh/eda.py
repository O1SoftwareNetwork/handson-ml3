#! /usr/bin/env python
# Copyright 2023 O1 Software Network. MIT licensed.

from pathlib import Path

import pandas as pd
from google.colab import drive

datasets = Path("~/gdrive/datasets").expanduser()
assert datasets.exists()
