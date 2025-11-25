#!/usr/bin/env python3
from datetime import datetime
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd

from .base import BaseTimeseriesGenerator


class PeriodicGenerator(BaseTimeseriesGenerator):
    """Generator for periodic signal"""

    def generate_timeseries(
        self,
        start_date: str,
        end_date: str,
        sampling_interval: str = "1h",
        dominant_period: str = "1d",
        base_value: float = 50,
        harmonics: int = 0,
        noise_level: float = 0.0,
        num_points: int | None = None,
        trend: str | None = None,
        trend_intensity: float = 0.0,
        main_phase_shift_rad: float = 0.0,
        trim_first_period: int = 0.3,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Generate a complex sinusoidal signal with specified parameters.

        Parameters:
        ----------
        start_date : str
            The start date of the signal in 'YYYY-MM-DD' format.
        end_date : str
            The end date of the signal in 'YYYY-MM-DD' format.
        sampling_interval : str
            Signal frequency in a string format like '1h', '30m', '15s', etc.
        dominant_period : str
            The dominant period of the signal, e.g., '1d' for daily, '1h' for hourly.
        base_value : float
            The central value around which the sinusoidal signal oscillates.
        harmonics : int
            The number of harmonics to add to the fundamental sine wave.
            Each harmonic will have a decreasing amplitude and increasing frequency.
        noise_level : float
            The amplitude of random noise to add to the signal.
        num_points : int, optional
            If specified, the number of data points in the generated signal.
            If None, the number of points is determined by the frequency and the date range.
        trend : str, optional
            The type of trend to add: "linear", "quadratic", or "exp".
            Defaults to None (no trend).
        trend_intensity : float, optional
            A value between 0 and 1 (inclusive) controlling the rate of trend increase/decrease.
            0 means no trend effect, 1 means maximum effect.
            For linear and quadratic, it scales the slope/curve.
            For exponential, it scales the exponent's growth rate.
        main_phase_shift_rad : float, optional
            Phase shift of the main sinusoidal component in radians.
        trim_first_period : float, optional
            A fraction of the last period to trim from the beginning of the signal.
        Returns:
        -------
        Tuple[pd.DataFrame, Dict[str, Any]]:
            A tuple containing:
            - A pandas DataFrame with two columns: 'TIMESTAMP' and 'VALUE'.
              'TIMESTAMP' contains the timestamps in Unix format,
              and 'VALUE' contains the generated signal values.
            - A dictionary with metadata about the generated signal.
        """
        if not (-1 <= trend_intensity <= 1):
            raise ValueError("trend_intensity must be between 0 and 1.")

        dominant_period_seconds = self.parse_frequency(dominant_period)

        start_timestamp = self.timestamp_to_unix(start_date)
        end_timestamp = self.timestamp_to_unix(end_date)
        sampling_interval_seconds = self.parse_frequency(sampling_interval)
        total_seconds = end_timestamp - start_timestamp
        n_cycles = total_seconds / dominant_period_seconds
        if abs(n_cycles - round(n_cycles)) < 0.05:
            end_timestamp += dominant_period_seconds * 0.37

        if num_points:
            timestamps = np.linspace(
                start_timestamp, end_timestamp, num_points, dtype=int
            )
        else:
            timestamps = np.arange(
                start_timestamp,
                end_timestamp + sampling_interval_seconds,
                sampling_interval_seconds,
                dtype=int,
            )

        delta_time = timestamps - timestamps[0]
        total_duration_seconds = (
            delta_time[-1]
            if len(delta_time) > 1
            else sampling_interval_seconds
        )
        normalized_time = (
            delta_time / total_duration_seconds
            if total_duration_seconds > 0
            else np.zeros_like(delta_time)
        )

        angular_frequency = 2 * np.pi / dominant_period_seconds

        signal_values = np.full(len(timestamps), base_value, dtype=float)

        fundamental_amplitude = base_value * 0.5
        signal_values += fundamental_amplitude * np.sin(
            angular_frequency * delta_time + main_phase_shift_rad
        )

        for i in range(1, harmonics + 1):
            harmonic_amplitude = fundamental_amplitude / (i + 1)
            signal_values += harmonic_amplitude * np.sin(
                (i + 1) * angular_frequency * delta_time
                + np.random.uniform(0, 2 * np.pi)
            )

        trend_component = np.zeros(len(timestamps))
        if trend and abs(trend_intensity) > 0:
            max_trend_effect = base_value * 1.5 * len(timestamps) / 2_000

            if trend == "linear":
                trend_component = (
                    max_trend_effect * trend_intensity * normalized_time
                )
            elif trend == "quadratic":
                trend_component = (
                    max_trend_effect * trend_intensity * (normalized_time**2)
                )
            elif trend == "exp":
                exp_rate = 5.0 * trend_intensity
                trend_component = (
                    max_trend_effect
                    * (np.exp(exp_rate * normalized_time) - 1)
                    / (np.exp(exp_rate) - 1)
                )
            else:
                print(
                    f"Warning: Unrecognized trend type '{trend}'. No trend applied."
                )

        signal_values += trend_component

        if noise_level > 0:
            noise = np.random.normal(
                0, noise_level * fundamental_amplitude, len(timestamps)
            )
            signal_values += noise

        min_val = signal_values.min()
        if min_val < 0:
            signal_values -= min_val

        if trim_first_period > 0:
            trim_length = int(
                trim_first_period
                * dominant_period_seconds
                / sampling_interval_seconds
            )
            timestamps = timestamps[trim_length:]
            signal_values = signal_values[trim_length:]
        df = pd.DataFrame({"TIMESTAMP": timestamps, "VALUE": signal_values})

        metadata = {
            "type": "sinusoidal",
            "params": {
                "start_date": start_date,
                "end_date": end_date,
                "sampling_interval": sampling_interval,
                "dominant_period": dominant_period,
                "base_value": base_value,
                "harmonics": harmonics,
                "noise_level": noise_level,
                "num_points": len(timestamps),
                "trend": trend,
                "trend_intensity": trend_intensity,
                "main_phase_shift_rad": main_phase_shift_rad,
            },
        }

        return df, metadata
