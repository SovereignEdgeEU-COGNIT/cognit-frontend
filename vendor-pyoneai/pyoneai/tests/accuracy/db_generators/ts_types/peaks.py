#!/usr/bin/env python3
import random
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

from .base import BaseTimeseriesGenerator


class PeaksGenerator(BaseTimeseriesGenerator):
    """Generator for time series with controllable peaks/spikes."""

    def generate_timeseries(
        self,
        start_date: str,
        end_date: str,
        frequency: str = "1h",
        base_value: float = 50.0,
        num_peaks: int = 3,
        min_peak_height: float = 80.0,
        max_peak_height: float = 120.0,
        min_peak_width: int = 3,
        max_peak_width: int = 8,
        peak_locations: List[int] = None,
        with_noise: bool = True,
        noise_level: float = 2.0,
        num_points: int = None,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Generate a time series with specified number of peaks.

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
        num_peaks : int
            Number of peaks to generate
        min_peak_height : float
            Minimum height of peaks
        max_peak_height : float
            Maximum height of peaks
        min_peak_width : int
            Minimum width of peaks (in number of data points)
        max_peak_width : int
            Maximum width of peaks (in number of data points)
        peak_locations : List[int], optional
            Specific locations for peaks in terms of indices.
            If not provided, random locations are generated.
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

        # Create base values
        values = np.ones(len(timestamps)) * base_value

        # Add peaks at the specified or random locations
        peak_records = []
        total_points = len(timestamps)

        if peak_locations is None:
            # Generate random peak locations if not provided
            if num_peaks > 0:
                peak_locations = sorted(
                    random.sample(range(total_points), num_peaks)
                )

        for peak_idx in peak_locations:
            if peak_idx < 0 or peak_idx >= total_points:
                continue  # Skip if index is out of bounds

            # Determine peak characteristics
            peak_height = random.uniform(min_peak_height, max_peak_height)
            peak_width = random.randint(min_peak_width, max_peak_width)

            # Ensure peak doesn't extend beyond array bounds
            peak_start = max(0, peak_idx - peak_width // 2)
            peak_end = min(total_points, peak_idx + peak_width // 2)

            # Create a Gaussian-shaped peak
            x = np.arange(peak_end - peak_start)
            center = len(x) / 2
            sigma = len(x) / 6  # Controls width of the peak
            peak_shape = np.exp(-0.5 * ((x - center) / sigma) ** 2)

            # Apply the peak
            for i, j in enumerate(range(peak_start, peak_end)):
                values[j] = (
                    base_value + (peak_height - base_value) * peak_shape[i]
                )

            # Record peak details for metadata
            peak_records.append(
                {
                    "index": peak_idx,
                    "timestamp": timestamps[peak_idx],
                    "datetime": self.unix_to_datetime(timestamps[peak_idx]),
                    "value": values[peak_idx],
                    "width": peak_width,
                    "height": peak_height,
                }
            )

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
            "type": "peaks",
            "params": {
                "start_date": start_date,
                "end_date": end_date,
                "base_value": base_value,
                "num_peaks": len(peak_records),
                "min_peak_height": min_peak_height,
                "max_peak_height": max_peak_height,
                "min_peak_width": min_peak_width,
                "max_peak_width": max_peak_width,
                "with_noise": with_noise,
                "noise_level": noise_level,
                "num_points": len(timestamps),
                "frequency": frequency,
                "peaks": peak_records,
            },
        }

        return df, metadata
