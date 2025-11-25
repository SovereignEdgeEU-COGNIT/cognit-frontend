#!/usr/bin/env python3
"""
Generator for time series with step changes.
"""

import datetime
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd

from .base import BaseTimeseriesGenerator


class StepChangeGenerator(BaseTimeseriesGenerator):
    """Generate time series with step changes."""

    def generate_timeseries(
        self, start_date: str, end_date: str, frequency: str, **kwargs
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Generate a time series with step change pattern.

        Parameters
        ----------
        start_date : str
            Start date in format 'YYYY-MM-DD HH:MM:SS'
        end_date : str
            End date in format 'YYYY-MM-DD HH:MM:SS'
        frequency : str
            Frequency of the time series (e.g., '30s', '5m', '1h', '1d')
        **kwargs : dict
            Additional parameters:
            - base_value : float, default=50.0
                Base value for the time series
            - step_point : int, default=None
                Point at which the step change occurs (index). If None, occurs at 50% of the time series.
            - step_size : float, default=20.0
                Size of the step change (positive for increase, negative for decrease)
            - with_noise : bool, default=True
                Whether to add random noise to the signal
            - noise_level : float, default=2.0
                Level of noise to add (standard deviation)

        Returns
        -------
        Tuple[pd.DataFrame, Dict[str, Any]]
            DataFrame with TIMESTAMP and VALUE columns, and metadata dictionary
        """
        # Extract parameters
        base_value = kwargs.get("base_value", 50.0)
        step_size = kwargs.get("step_size", 20.0)
        with_noise = kwargs.get("with_noise", True)
        noise_level = kwargs.get("noise_level", 2.0)

        # Generate time range
        start_ts = self.timestamp_to_unix(start_date)
        end_ts = self.timestamp_to_unix(end_date)
        freq_seconds = self.parse_frequency(frequency)

        timestamps = np.arange(start_ts, end_ts + 1, freq_seconds)
        num_points = len(timestamps)

        # Determine step point (default to middle of series if not specified)
        step_point = kwargs.get("step_point")
        if step_point is None:
            step_point = num_points // 2
        else:
            step_point = min(step_point, num_points - 1)

        # Create step change pattern
        values = np.ones(num_points) * base_value
        values[step_point:] += step_size

        # Add noise if requested
        if with_noise:
            noise = np.random.normal(0, noise_level, num_points)
            values += noise

        # Ensure non-negative values
        values = np.maximum(values, 0)

        # Create DataFrame
        df = pd.DataFrame({"TIMESTAMP": timestamps, "VALUE": values})

        # Get the step datetime
        step_datetime = datetime.datetime.fromtimestamp(
            timestamps[step_point]
        ).strftime("%Y-%m-%d %H:%M:%S")

        # Create metadata
        metadata = {
            "type": "step_change",
            "params": {
                "start_date": start_date,
                "end_date": end_date,
                "base_value": base_value,
                "step_point": step_point,
                "step_datetime": step_datetime,
                "step_size": step_size,
                "with_noise": with_noise,
                "noise_level": noise_level,
                "num_points": num_points,
                "frequency": frequency,
            },
        }

        # Add path to database if provided
        if "database_path" in kwargs:
            metadata["database_path"] = kwargs["database_path"]

        return df, metadata
