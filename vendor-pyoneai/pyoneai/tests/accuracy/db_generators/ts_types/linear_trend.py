#!/usr/bin/env python3
"""
Generator for time series with linear trends.
"""

from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd

from .base import BaseTimeseriesGenerator


class LinearTrendGenerator(BaseTimeseriesGenerator):
    """Generate time series with linear trends."""

    def generate_timeseries(
        self, start_date: str, end_date: str, frequency: str, **kwargs
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Generate a time series with linear trend pattern.

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
            - slope : float, default=0.5
                Slope of the linear trend (positive for growing, negative for declining)
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
        slope = kwargs.get("slope", 0.5)
        with_noise = kwargs.get("with_noise", True)
        noise_level = kwargs.get("noise_level", 2.0)

        # Generate time range
        start_ts = self.timestamp_to_unix(start_date)
        end_ts = self.timestamp_to_unix(end_date)
        freq_seconds = self.parse_frequency(frequency)

        timestamps = np.arange(start_ts, end_ts + 1, freq_seconds)
        num_points = len(timestamps)

        # Create linear trend
        t = np.arange(num_points)
        trend = slope * t
        values = base_value + trend

        # Add noise if requested
        if with_noise:
            noise = np.random.normal(0, noise_level, num_points)
            values += noise

        # Ensure non-negative values
        values = np.maximum(values, 0)

        # Create DataFrame
        df = pd.DataFrame({"TIMESTAMP": timestamps, "VALUE": values})

        # Create metadata
        metadata = {
            "type": "linear_trend",
            "params": {
                "start_date": start_date,
                "end_date": end_date,
                "base_value": base_value,
                "slope": slope,
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
