import argparse
import logging
from datetime import datetime, timedelta

from pyoneai.core import Entity, EntityType, EntityUID
from pyoneai.core.time import Period
from pyoneai.core.tsnumpy.timeseries import Timeseries
from pyoneai.tests.accuracy.config import (
    DATA_FILE,
    DUMMY_ENTITY_ID,
    REPORT_DIR,
)
from pyoneai.tests.accuracy.methods import get_methods
from pyoneai.tests.accuracy.utils.io import get_metric_date_range_from_db
from pyoneai.tests.accuracy.utils.time import (
    measure_time,
    parse_timedelta_str_to_seconds,
)

log = logging.getLogger("accuracy-test")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run accuracy tests for the PyOneAI SDK."
    )
    parser.add_argument(
        "--horizon",
        "-H",
        type=parse_timedelta_str_to_seconds,
        default="10m",
        help="Forecast horizon (default: 10 minutes)",
    )
    parser.add_argument(
        "--method",
        "-m",
        nargs="*",
    )
    parser.add_argument(
        "--freq",
        "-f",
        type=parse_timedelta_str_to_seconds,
        default="30s",
        help="Frequency of the data (default: 30 seconds)",
    )
    parser.add_argument(
        "--lookback",
        "-l",
        type=parse_timedelta_str_to_seconds,
        default="60m",
        help="Lookback period (default: 60 minutes)",
    )
    parser.add_argument(
        "--step",
        "-s",
        type=int,
        default=1,
        help="Step size for the moving window forecast (default: 1)",
    )
    parser.add_argument(
        "--no_seasonality_metrics",
        "-nsm",
        action="store_true",
        default=True,
        help="Do not run experiments for time series with seasonality (default: False)",
    )
    parser.add_argument(
        "--hourly_metrics",
        "-hm",
        action="store_true",
        default=False,
        help="Run experiments for time series with seasonality defined as hourly (default: False)",
    )
    parser.add_argument(
        "--daily_metrics",
        "-dm",
        action="store_true",
        default=False,
        help="Run experiments for time series with seasonality defined as daily (default: False)",
    )
    parser.add_argument(
        "--weekly_metrics",
        "-wm",
        action="store_true",
        default=False,
        help="Run experiments for time series with seasonality defined as weekly (default: False)",
    )
    parser.add_argument(
        "-monthly_metrics",
        "--mm",
        action="store_true",
        default=False,
        help="Run experiments for time series with seasonality defined as monthly (default: False)",
    )
    parser.add_argument(
        "--plot_all",
        "-pa",
        action="store_true",
        default=False,
        help="Plot all windows in a single figure (default: False)",
    )
    return parser.parse_args()


def _get_start_end_dates(
    metric_name: str, entity, lookback_seconds: int, horizon_seconds: int
):
    start_date, end_date = get_metric_date_range_from_db(metric_name, entity)
    valid_start_date = start_date + timedelta(seconds=lookback_seconds)
    valid_end_date = end_date - timedelta(seconds=horizon_seconds)
    if valid_start_date >= valid_end_date:
        raise ValueError(
            f"Invalid date range for metric '{metric_name}' on entity '{entity.uid.id}': "
            f"start date {valid_start_date} is not before end date {valid_end_date}"
        )
    if start_date is None or end_date is None:
        raise ValueError(
            f"Metric '{metric_name}' has no data for entity '{entity.uid.id}'"
        )
    return start_date, end_date, valid_start_date, valid_end_date


def plot_single_window(
    window_start_date: datetime,
    reference: Timeseries,
    forecast: Timeseries,
    lookback: Timeseries,
    metric_name: str,
    entity_id: str,
    method_name: str,
    horizon_seconds: int,
):
    import matplotlib.pyplot as plt

    target_file = (
        REPORT_DIR
        / f"horizon_{horizon_seconds}s"
        / f"entity_id_{entity_id}"
        / method_name
        / metric_name
        / f"window_{window_start_date}.png"
    )
    target_file.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        reference.time_index,
        reference.values.squeeze(),
        label="Reference",
        color="blue",
    )
    ax.plot(
        forecast.time_index,
        forecast.values.squeeze(),
        label="Forecast",
        color="orange",
        linestyle="--",
    )
    ax.plot(
        lookback.time_index,
        lookback.values.squeeze(),
        label="Lookback",
        color="green",
    )
    ax.set_title(
        f"{metric_name} Forecast vs Reference for Entity {entity_id} using {method_name} (Window {window_start_date})"
    )
    ax.set_xlabel("Time")
    ax.set_ylabel(metric_name)
    ax.legend()
    ax.grid()
    fig.savefig(target_file)
    plt.close(fig)


def update_quality_report(
    entity: Entity,
    metric_name: str,
    method_name: str,
    window_start_date: datetime,
    horizon_seconds: int,
    mae: float,
    rmse: float,
    mape: float,
    elapsed_time: float = 0.0,
):
    import csv

    report_file = (
        REPORT_DIR
        / f"horizon_{horizon_seconds}s"
        / f"entity_id_{entity.uid.id}"
        / method_name
        / metric_name
        / "quality_report.csv"
    )
    report_file.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["window_start_date", "mae", "rmse", "mape", "elapsed_time"]
    if not report_file.exists():
        with open(report_file, "w") as f:
            csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
            csv_writer.writeheader()
    else:
        with open(report_file, "a") as f:
            csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
            csv_writer.writerow(
                {
                    "window_start_date": window_start_date.isoformat(),
                    "mae": mae,
                    "rmse": rmse,
                    "mape": mape,
                    "elapsed_time": elapsed_time,
                }
            )


def run_windowed_test(
    entity: Entity,
    metric_name: str,
    lookback_seconds: int,
    horizon_seconds: int,
    frequency_seconds: int,
    step: int = 1,
    plot_all: bool = False,
):
    start_date, end_date, valid_start_date, valid_end_date = (
        _get_start_end_dates(
            metric_name, entity, lookback_seconds, horizon_seconds
        )
    )
    forecast_start_date = valid_start_date
    while forecast_start_date < valid_end_date:
        log.info(
            f"Running windowed test for {metric_name} on entity {entity.uid.id} at {forecast_start_date}"
        )
        with measure_time() as timer:
            forecast = entity[metric_name][
                Period(
                    origin=forecast_start_date
                    - timedelta(seconds=frequency_seconds),
                    value=slice(
                        forecast_start_date,
                        forecast_start_date
                        + timedelta(seconds=horizon_seconds),
                        timedelta(seconds=frequency_seconds),
                    ),
                )
            ]
        reference = entity[metric_name][
            Period(
                origin=forecast_start_date
                + timedelta(seconds=horizon_seconds),
                value=slice(
                    forecast_start_date,
                    forecast_start_date + timedelta(seconds=horizon_seconds),
                    timedelta(seconds=frequency_seconds),
                ),
            )
        ]
        lookback = entity[metric_name][
            Period(
                origin=forecast_start_date,
                value=slice(
                    forecast_start_date - timedelta(seconds=lookback_seconds),
                    forecast_start_date,
                    timedelta(seconds=frequency_seconds),
                ),
            )
        ]
        if plot_all:
            plot_single_window(
                forecast_start_date,
                reference,
                forecast,
                lookback,
                metric_name,
                entity.uid.id,
                entity._pred._prediction_model.model_config.model_class,
                horizon_seconds,
            )
        mae = Timeseries.mae(forecast, reference)
        mape = Timeseries.mape(forecast, reference)
        rmse = Timeseries.rmse(forecast, reference)
        log.info(f"MAE: {mae}, RMSE: {rmse}, MAPE: {mape}")
        update_quality_report(
            entity,
            metric_name,
            entity._pred._prediction_model.model_config.model_class,
            forecast_start_date,
            horizon_seconds,
            mae,
            rmse,
            mape,
            elapsed_time=timer.elapsed_time,
        )
        forecast_start_date += timedelta(seconds=step * frequency_seconds)


def get_entity(metrics):
    return Entity(
        uid=EntityUID(type=EntityType.VIRTUAL_MACHINE, id=DUMMY_ENTITY_ID),
        metrics=metrics,
        monitoring={"db_path": DATA_FILE, "monitor_interval": 30},
    )


def run_accuracy_tests(
    horizon_seconds: int,
    frequency_seconds: int,
    lookback_seconds: int,
    methods: list[str],
    step: int = 1,
    no_seasonality_metrics: bool = True,
    hourly_seasonality_metrics: bool = False,
    daily_seasonality_metrics: bool = False,
    monthly_seasonality_metrics: bool = False,
    plot_all: bool = False,
):
    from pyoneai.tests.accuracy.config import (
        DAILY_SEASONALITY_METRICS,
        HOURLY_SEASONALITY_METRICS,
        MONTHLY_SEASONALITY_METRICS,
        NO_SEASONALITY_METRICS,
    )

    metrics = {}
    if no_seasonality_metrics:
        log.info("Running accuracy tests for metrics with no seasonalty")
        metrics.update(NO_SEASONALITY_METRICS)
    if hourly_seasonality_metrics:
        log.info("Running accuracy tests for metrics with hourly seasonality")
        metrics.update(HOURLY_SEASONALITY_METRICS)
    if daily_seasonality_metrics:
        log.info("Running accuracy tests for metrics with daily seasonality")
        metrics.update(DAILY_SEASONALITY_METRICS)
    if monthly_seasonality_metrics:
        log.info("Running accuracy tests for metrics with monthly seasonality")
        metrics.update(MONTHLY_SEASONALITY_METRICS)
    entity = get_entity(metrics)

    for metric in metrics.keys():
        log.info(f"Running short-term accuracy tests for metric: {metric}")
        for method in get_methods(methods):
            log.info(
                f"Using prediction method: {method.model_config.model_class}"
            )
            entity._pred._prediction_model = method
            entity._pred._prediction_model.model_config.sequence_length = int(
                lookback_seconds / frequency_seconds
            )
            run_windowed_test(
                entity=entity,
                metric_name=metric,
                lookback_seconds=lookback_seconds,
                horizon_seconds=horizon_seconds,
                frequency_seconds=frequency_seconds,
                step=step,
                plot_all=plot_all,
            )


if __name__ == "__main__":
    arguments = parse_args()
    run_accuracy_tests(
        horizon_seconds=arguments.horizon,
        frequency_seconds=arguments.freq,
        lookback_seconds=arguments.lookback,
        methods=arguments.method,
        step=arguments.step,
        no_seasonality_metrics=arguments.no_seasonality_metrics,
        hourly_seasonality_metrics=arguments.hourly_metrics,
        daily_seasonality_metrics=arguments.daily_metrics,
        monthly_seasonality_metrics=arguments.mm,
        plot_all=arguments.plot_all,
    )
