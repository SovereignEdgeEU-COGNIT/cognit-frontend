import importlib
import importlib.resources
import logging
from datetime import datetime

import numpy as np
import pandas as pd
import ts_types as generators

from pyoneai.core import EntityType, EntityUID, MetricAttributes, Timeseries

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

START_DATE = "2025-01-01 00:10:00"
END_DATE = "2025-05-23 10:35:45"
FREQ = "30s"
ENTITY_ID = 100
DB_PATH = importlib.resources.files("pyoneai").joinpath(
    "tests", "accuracy", "resources", "data.db"
)

# NOTE: Any new characteristics should be defined here
TIMESERIES = {
    "hourly linear pure increasing": (
        generators.PeriodicGenerator(),
        {
            "start_date": START_DATE,
            "end_date": END_DATE,
            "sampling_interval": FREQ,
            "dominant_period": "1h",
            "base_value": 200.0,
            "main_phase_shift_rad": np.pi / 6,
            "harmonics": 0,
            "trend": "linear",
            "trend_intensity": 0.8,
            "noise_level": 0.0,
        },
    ),
    "hourly linear pure decreasing": (
        generators.PeriodicGenerator(),
        {
            "start_date": START_DATE,
            "end_date": END_DATE,
            "sampling_interval": FREQ,
            "dominant_period": "1h",
            "base_value": 600.0,
            "main_phase_shift_rad": np.pi / 6,
            "harmonics": 0,
            "trend": "linear",
            "trend_intensity": -0.8,
            "noise_level": 0.0,
        },
    ),
    "hourly linear 4 harmonics increasing": (
        generators.PeriodicGenerator(),
        {
            "start_date": START_DATE,
            "end_date": END_DATE,
            "sampling_interval": FREQ,
            "dominant_period": "1h",
            "base_value": 50.0,
            "main_phase_shift_rad": np.pi / 6,
            "harmonics": 4,
            "trend": "linear",
            "trend_intensity": 0.9,
            "noise_level": 0.1,
        },
    ),
    "daily exponential 4 harmonics increasing": (
        generators.PeriodicGenerator(),
        {
            "start_date": START_DATE,
            "end_date": END_DATE,
            "sampling_interval": FREQ,
            "dominant_period": "1d",
            "base_value": 50.0,
            "main_phase_shift_rad": np.pi / 6,
            "harmonics": 4,
            "trend": "exp",
            "trend_intensity": 0.002,
            "noise_level": 0.1,
        },
    ),
    "daily linear 2 harmonics increasing": (
        generators.PeriodicGenerator(),
        {
            "start_date": START_DATE,
            "end_date": END_DATE,
            "sampling_interval": FREQ,
            "dominant_period": "1d",
            "base_value": 50.0,
            "main_phase_shift_rad": np.pi / 6,
            "harmonics": 2,
            "trend": "linear",
            "trend_intensity": 0.07,
            "noise_level": 0.1,
        },
    ),
    "daily linear 2 harmonics": (
        generators.PeriodicGenerator(),
        {
            "start_date": START_DATE,
            "end_date": END_DATE,
            "sampling_interval": FREQ,
            "dominant_period": "1d",
            "base_value": 50.0,
            "main_phase_shift_rad": np.pi / 6,
            "harmonics": 2,
            "trend": None,
            "trend_intensity": 0.0,
            "noise_level": 0.1,
        },
    ),
    "bidaily exp 2 harmonics increasing": (
        generators.PeriodicGenerator(),
        {
            "start_date": START_DATE,
            "end_date": END_DATE,
            "sampling_interval": FREQ,
            "dominant_period": "2d",
            "base_value": 50.0,
            "main_phase_shift_rad": np.pi / 5,
            "harmonics": 7,
            "trend": "exp",
            "trend_intensity": 0.001,
            "noise_level": 0.2,
        },
    ),
    "monthly linear 4 harmonics increasing": (
        generators.PeriodicGenerator(),
        {
            "start_date": START_DATE,
            "end_date": END_DATE,
            "sampling_interval": FREQ,
            "dominant_period": "1M",
            "base_value": 50.0,
            "main_phase_shift_rad": np.pi / 6,
            "harmonics": 4,
            "trend": "linear",
            "trend_intensity": 0.05,
            "noise_level": 0.1,
        },
    ),
    "monthly linear 4 harmonics decreasing": (
        generators.PeriodicGenerator(),
        {
            "start_date": START_DATE,
            "end_date": END_DATE,
            "sampling_interval": FREQ,
            "dominant_period": "1M",
            "base_value": 50.0,
            "main_phase_shift_rad": np.pi / 6,
            "harmonics": 4,
            "trend": "linear",
            "trend_intensity": -0.03,
            "noise_level": 0.1,
        },
    ),
    "monthly linear 2 harmonics": (
        generators.PeriodicGenerator(),
        {
            "start_date": START_DATE,
            "end_date": END_DATE,
            "sampling_interval": FREQ,
            "dominant_period": "1M",
            "base_value": 50.0,
            "main_phase_shift_rad": np.pi / 6,
            "harmonics": 2,
            "trend": None,
            "trend_intensity": 0.0,
            "noise_level": 0.1,
        },
    ),
    "weekly linear 2 harmonics increasing": (
        generators.PeriodicGenerator(),
        {
            "start_date": START_DATE,
            "end_date": END_DATE,
            "sampling_interval": FREQ,
            "dominant_period": "7d",
            "base_value": 50.0,
            "main_phase_shift_rad": np.pi / 6,
            "harmonics": 2,
            "trend": "linear",
            "trend_intensity": 0.01,
            "noise_level": 0.4,
        },
    ),
    "weekly exp 5 harmonics increasing": (
        generators.PeriodicGenerator(),
        {
            "start_date": START_DATE,
            "end_date": END_DATE,
            "sampling_interval": FREQ,
            "dominant_period": "7d",
            "base_value": 50.0,
            "main_phase_shift_rad": np.pi / 2,
            "harmonics": 5,
            "trend": "exp",
            "trend_intensity": 0.001,
            "noise_level": 0.2,
        },
    ),
    "weekly linear 3 harmonics decreasing": (
        generators.PeriodicGenerator(),
        {
            "start_date": START_DATE,
            "end_date": END_DATE,
            "sampling_interval": FREQ,
            "dominant_period": "7d",
            "base_value": 50.0,
            "main_phase_shift_rad": np.pi / 6,
            "harmonics": 3,
            "trend": "linear",
            "trend_intensity": -0.01,
            "noise_level": 0.2,
        },
    ),
    "linear increasing": (
        generators.TrendWithGapsGenerator(),
        {
            "start_date": START_DATE,
            "end_date": END_DATE,
            "frequency": FREQ,
            "with_noise": True,
            "num_gaps": 0,
            "noise_level": 10.0,
        },
    ),
    "constant no noise": (
        generators.ConstantGenerator(),
        {
            "start_date": START_DATE,
            "end_date": END_DATE,
            "frequency": FREQ,
            "base_value": 50.0,
            "with_noise": False,
        },
    ),
    "constant": (
        generators.ConstantGenerator(),
        {
            "start_date": START_DATE,
            "end_date": END_DATE,
            "frequency": FREQ,
            "with_noise": True,
            "noise_level": 1.0,
            "base_value": 75.0,
        },
    ),
}


def create_db_with_timeseries(
    db_path: str, data: pd.DataFrame, metric_name: str
):
    times = np.array(
        [datetime.fromtimestamp(d) for d in data["TIMESTAMP"].values],
        dtype=object,
    )
    ts = Timeseries(
        time_idx=times,
        metric_idx=np.array([MetricAttributes(name=metric_name)]),
        entity_uid_idx=np.array(
            [EntityUID(id=ENTITY_ID, type=EntityType.VIRTUAL_MACHINE)]
        ),
        data=data["VALUE"].values.reshape(-1, 1, 1),
    )
    ts.write_to_db(db_path, retention=None, suffix="monitoring")


def generate_db(conf: dict):
    for kind, (generator, params) in conf.items():
        data, _ = generator.generate_timeseries(**params)
        create_db_with_timeseries(str(DB_PATH), data, kind)


if __name__ == "__main__":
    import os

    try:
        os.remove(DB_PATH)
    except FileNotFoundError:
        pass
    generate_db(TIMESERIES)
