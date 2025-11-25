import importlib

from pyoneai.core import (
    MetricAttributes,
    MetricType,
)

DUMMY_ENTITY_ID: int = 100
ACCURACY_TEST_DIR = importlib.resources.files("pyoneai").joinpath(
    "tests", "accuracy"
)
RESOURCES_DIR = ACCURACY_TEST_DIR / "resources"
DATA_FILE = RESOURCES_DIR / "data.db"
REPORT_DIR = ACCURACY_TEST_DIR / "report"

NO_SEASONALITY_METRICS = {
    "linear increasing": MetricAttributes(
        name="linear increasing", type=MetricType.GAUGE
    ),
    "constant no noise": MetricAttributes(
        name="constant no noise", type=MetricType.GAUGE
    ),
    "constant": MetricAttributes(name="constant", type=MetricType.GAUGE),
}

HOURLY_SEASONALITY_METRICS = {
    "hourly linear pure increasing": MetricAttributes(
        name="hourly linear pure increasing", type=MetricType.GAUGE
    ),
    "hourly linear pure decreasing": MetricAttributes(
        name="hourly linear pure decreasing", type=MetricType.GAUGE
    ),
    "hourly linear 4 harmonics increasing": MetricAttributes(
        name="hourly linear 4 harmonics increasing", type=MetricType.GAUGE
    ),
    "hourly linear 5 harmonics decreasing": MetricAttributes(
        name="hourly linear 5 harmonics decreasing", type=MetricType.GAUGE
    ),
    "half hourly linear 2 harmonics increasing": MetricAttributes(
        name="half hourly linear 2 harmonics increasing", type=MetricType.GAUGE
    ),
}

DAILY_SEASONALITY_METRICS = {
    "daily exponential 4 harmonics increasing": MetricAttributes(
        name="daily exponential 4 harmonics increasing", type=MetricType.GAUGE
    ),
    "daily linear 2 harmonics increasing": MetricAttributes(
        name="daily linear 2 harmonics increasing", type=MetricType.GAUGE
    ),
    "daily linear 2 harmonics": MetricAttributes(
        name="daily linear 2 harmonics", type=MetricType.GAUGE
    ),
    "bidaily exp 2 harmonics increasing": MetricAttributes(
        name="bidaily exp 2 harmonics increasing", type=MetricType.GAUGE
    ),
}
WEEKLY_SEASONALITY_METRICS = {
    "weekly linear 2 harmonics increasing": MetricAttributes(
        name="weekly linear 2 harmonics increasing", type=MetricType.GAUGE
    ),
    "weekly exp 5 harmonics increasing": MetricAttributes(
        name="weekly exp 5 harmonics increasing", type=MetricType.GAUGE
    ),
    "weekly linear 3 harmonics decreasing": MetricAttributes(
        name="weekly linear 3 harmonics decreasing", type=MetricType.GAUGE
    ),
}
MONTHLY_SEASONALITY_METRICS = {
    "monthly linear 4 harmonics increasing": MetricAttributes(
        name="monthly linear 4 harmonics increasing", type=MetricType.GAUGE
    ),
    "monthly linear 4 harmonics decreasing": MetricAttributes(
        name="monthly linear 4 harmonics decreasing", type=MetricType.GAUGE
    ),
    "monthly linear 2 harmonics": MetricAttributes(
        name="monthly linear 2 harmonics", type=MetricType.GAUGE
    ),
}
