from datetime import timedelta

import matplotlib.pyplot as plt
import numpy as np
import pytest

from pyoneai.core import Entity, Period
from pyoneai.core.tsnumpy.timeseries import Timeseries

from .config import LONG_TERM_METRICS, SHORT_TERM_METRICS
from .utils.io import (
    get_metric_date_range_from_db,
    get_vm_entities_longterm,
    get_vm_entities_shortterm,
    save_plots,
    save_result,
)
from .utils.time import measure_time


class TestAccuracy:

    @pytest.fixture(autouse=True)
    def setup(self, pytestconfig):
        self.freq = pytestconfig.getoption("resolution")
        self.history = pytestconfig.getoption("history")

    @pytest.mark.parametrize("metric_name", SHORT_TERM_METRICS.keys())
    @pytest.mark.parametrize("entity", get_vm_entities_shortterm())
    def test_vm_shortterm(
        self,
        metric_name,
        entity,
        prediction_model,
        vm_config_short,
    ):
        entity._pred._prediction_model = prediction_model
        entity._pred._prediction_model.model_config.sequence_length = (
            vm_config_short["sequence_length"]
        )
        result, figs = self.run_single_metric_test(
            metric_name,
            entity,
            vm_config_short["forecast_lookback_seconds"],
            vm_config_short["forecast_period_seconds"],
            vm_config_short["sequence_length"],
            reconstruct=True,
        )
        save_result(
            result, metric_name, entity.uid.id, type(prediction_model).__name__
        )
        if figs:
            save_plots(
                figs,
                metric_name,
                entity.uid.id,
                type(prediction_model).__name__,
                longterm=False,
            )

    @pytest.mark.parametrize("metric_name", LONG_TERM_METRICS.keys())
    @pytest.mark.parametrize("entity", get_vm_entities_longterm())
    def test_vm_longterm(
        self,
        metric_name,
        entity,
        prediction_model,
        vm_config_long,
    ):
        entity._pred._prediction_model = prediction_model
        entity._pred._prediction_model.model_config.sequence_length = (
            vm_config_long["sequence_length"]
        )
        result, figs = self.run_single_metric_test(
            metric_name,
            entity,
            vm_config_long["forecast_lookback_seconds"],
            vm_config_long["forecast_period_seconds"],
            vm_config_long["sequence_length"],
            # NOTE: Skip reconstruction for long-term forecasts to save time
            reconstruct=False,
        )
        save_result(
            result, metric_name, entity.uid.id, type(prediction_model).__name__
        )
        if figs:
            save_plots(
                figs,
                metric_name,
                entity.uid.id,
                type(prediction_model).__name__,
                longterm=True,
            )

    def run_single_metric_test(
        self,
        metric_name: str,
        entity: Entity,
        forecast_lookback_seconds,
        forecast_period_seconds,
        sequence_length,
        reconstruct: bool = True,
    ):
        fig = result = None
        start_date, end_date = get_metric_date_range_from_db(
            metric_name, entity
        )
        if self.history is None:
            sample_period = Period(
                origin=end_date,
                value=slice(
                    start_date, end_date, timedelta(seconds=self.freq)
                ),
            )
        else:
            sample_period = Period(
                origin=end_date,
                value=slice(
                    end_date
                    - timedelta(seconds=(self.history - 1) * self.freq),
                    end_date,
                    timedelta(seconds=self.freq),
                ),
            )
        all_data = entity[metric_name][sample_period]
        if len(all_data) < 2:
            pytest.fail(f"Not enough data points for '{metric_name}'")
            return

        time_idx = all_data.time_index
        forecast_period_items = forecast_period_seconds // self.freq
        if len(time_idx) > (forecast_period_items + 1 + sequence_length):
            history_start = time_idx[
                -(forecast_period_items + 1) - sequence_length
            ]
        else:
            history_start = time_idx[0]
        history_end = time_idx[-(forecast_period_items + 1)]

        actual_start = forecast_start = time_idx[-(forecast_period_items)]
        actual_end = forecast_end = time_idx[-1]

        history_period = Period(
            origin=history_end,
            value=slice(
                history_start,
                history_end,
                timedelta(seconds=self.freq),
            ),
        )
        prediction_forecast_period = Period(
            origin=forecast_start - timedelta(seconds=self.freq),
            value=slice(
                forecast_start,
                forecast_end,
                timedelta(seconds=self.freq),
            ),
        )
        reference_forecast_period = Period(
            origin=actual_end - timedelta(seconds=self.freq),
            value=slice(
                actual_start,
                actual_end,
                timedelta(seconds=self.freq),
            ),
        )
        # NOTE: we use `all_data` instead of
        # `entity[metric_name][history_period]` for historical
        # data to avoid re-fetching data from the database and
        # preprocessing it multiple times
        history_ts = all_data[history_period]
        reference_ts = all_data[reference_forecast_period]
        with measure_time() as timer:
            predicted_ts = entity[metric_name][prediction_forecast_period]

        prediction_model = entity[
            metric_name
        ].accessor._predictor_accessor._prediction_model
        reconstructed_history_ts = None
        if reconstruct:
            # NOTE: we skip reconstruction for long term forecasts
            # to save much time
            reconstructed_history_ts = prediction_model.predict(
                history_ts, forecast_index=history_ts._time_idx
            )

        if len(reference_ts) >= 2 and len(predicted_ts) >= 2:
            window_mape = Timeseries.mape(predicted_ts, reference_ts)
            fig = TestAccuracy._plot_timeseries(
                history_ts,
                predicted_ts,
                reference_ts,
                reconstructed_history_ts,
                last=-1,
            )
            window_rmse = Timeseries.rmse(predicted_ts, reference_ts)
            window_mae = Timeseries.mae(predicted_ts, reference_ts)
            result = {
                "vm_id": str(entity.uid.id),
                "metric": metric_name,
                "mape": window_mape,
                "rmse": window_rmse,
                "mae": window_mae,
                "historical_period_start": history_start,
                "historical_period_end": history_end,
                "forecast_period_start": forecast_start,
                "forecast_period_end": forecast_end,
                "elapsed_time": timer.elapsed_time,
            }
        return result, fig

    @staticmethod
    def _plot_timeseries(
        history, forecast, true, reconstructed_history=None, last: int = 10
    ):
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(
            history.time_index[-last:],
            history.values.squeeze()[-last:],
            linestyle="-",
            color="b",
            label="history",
        )
        ax.plot(
            forecast.time_index,
            forecast.values.squeeze(),
            linestyle="--",
            color="g",
            label="forecast",
        )
        ax.plot(
            true.time_index,
            true.values.squeeze(),
            linestyle="-",
            color="k",
            label="true",
            alpha=0.5,
        )
        if reconstructed_history is not None:
            ax.plot(
                reconstructed_history.time_index,
                reconstructed_history.values.squeeze(),
                linestyle="--",
                color="r",
                label="reconstructed",
                alpha=0.5,
            )
        ax.legend()
        return fig
