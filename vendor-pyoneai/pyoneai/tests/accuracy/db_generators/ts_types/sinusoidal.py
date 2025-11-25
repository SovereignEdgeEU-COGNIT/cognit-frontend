#!/usr/bin/env python3
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd

from .base import BaseTimeseriesGenerator


class SinusoidalGenerator(BaseTimeseriesGenerator):
    """Generator for sinusoidal time series with daily and weekly patterns."""

    def generate_timeseries(
        self,
        start_date: str,
        end_date: str,
        frequency: str = "1h",
        base_value: float = 50.0,
        daily_amplitude: float = 10.0,
        weekly_amplitude: float = 5.0,
        with_noise: bool = True,
        noise_level: float = 2.0,
        num_points: int = None,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Generate a time series with sinusoidal patterns (daily and weekly cycles).

        Parameters
        ----------
        start_date : str
            Start date in format 'YYYY-MM-DD HH:MM:SS'
        end_date : str
            End date in format 'YYYY-MM-DD HH:MM:SS'
        frequency : str
            Frequency of the time series (e.g., '30s', '5m', '1h', '1d')
        base_value : float
            Base value for the time series
        daily_amplitude : float
            Amplitude of daily pattern
        weekly_amplitude : float
            Amplitude of weekly pattern
        with_noise : bool
            Whether to add noise
        noise_level : float
            Standard deviation of noise
        num_points : int, optional
            Number of data points; if not provided, calculated from frequency

        Returns
        -------
        Tuple[pd.DataFrame, Dict[str, Any]]
            DataFrame with TIMESTAMP and VALUE columns, and metadata dictionary
        """
        # Convert dates to Unix timestamps
        start_timestamp = self.timestamp_to_unix(start_date)
        end_timestamp = self.timestamp_to_unix(end_date)

        # Calculate interval in seconds from frequency
        interval_seconds = self.parse_frequency(frequency)

        # Create timestamps
        if num_points:
            timestamps = np.linspace(
                start_timestamp, end_timestamp, num_points, dtype=int
            )
        else:
            timestamps = np.arange(
                start_timestamp,
                end_timestamp + interval_seconds,
                interval_seconds,
                dtype=int,
            )

        # Number of points
        t = np.arange(len(timestamps))

        # Daily pattern - scale according to frequency
        points_per_day = 24 * 3600 / interval_seconds
        daily_pattern = daily_amplitude * np.sin(
            2 * np.pi * t / points_per_day
        )

        # Weekly pattern - scale according to frequency
        points_per_week = 7 * points_per_day
        weekly_pattern = weekly_amplitude * np.sin(
            2 * np.pi * t / points_per_week
        )

        # Combine patterns
        values = base_value + daily_pattern + weekly_pattern

        # Add noise if requested
        if with_noise:
            noise = np.random.normal(0, noise_level, len(timestamps))
            values += noise

        # Ensure non-negative values
        values = np.maximum(values, 0)

        # Create DataFrame
        df = pd.DataFrame({"TIMESTAMP": timestamps, "VALUE": values})

        # Create metadata
        metadata = {
            "type": "sinusoidal",
            "params": {
                "start_date": start_date,
                "end_date": end_date,
                "base_value": base_value,
                "daily_amplitude": daily_amplitude,
                "weekly_amplitude": weekly_amplitude,
                "with_noise": with_noise,
                "noise_level": noise_level,
                "num_points": len(timestamps),
                "frequency": frequency,
            },
        }

        return df, metadata
