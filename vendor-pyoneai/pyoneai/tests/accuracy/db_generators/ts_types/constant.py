#!/usr/bin/env python3
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd

from .base import BaseTimeseriesGenerator


class ConstantGenerator(BaseTimeseriesGenerator):
    """Generator for constant time series with optional noise."""

    def generate_timeseries(
        self,
        start_date: str,
        end_date: str,
        frequency: str = "1h",
        base_value: float = 50.0,
        with_noise: bool = False,
        noise_level: float = 1.0,
        num_points: int = None,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Generate a time series with constant values.

        Parameters
        ----------
        start_date : str
            Start date in format 'YYYY-MM-DD HH:MM:SS'
        end_date : str
            End date in format 'YYYY-MM-DD HH:MM:SS'
        frequency : str
            Frequency of the time series (e.g., '30s', '5m', '1h', '1d')
        value : float
            Constant value for the time series
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

        # Create constant values
        values = np.ones(len(timestamps)) * base_value

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
            "type": "constant",
            "params": {
                "start_date": start_date,
                "end_date": end_date,
                "base_value": base_value,
                "with_noise": with_noise,
                "noise_level": noise_level,
                "num_points": len(timestamps),
                "frequency": frequency,
            },
        }

        return df, metadata
