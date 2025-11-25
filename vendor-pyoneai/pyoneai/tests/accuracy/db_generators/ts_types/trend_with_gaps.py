import random
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd

from .base import BaseTimeseriesGenerator


class TrendWithGapsGenerator(BaseTimeseriesGenerator):
    """Generator for monotonically increasing trend time series with configurable seasonal zero-value intervals.

    Creates a time series with a consistent upward trend.
    Specified number of zero-value intervals (`num_gaps`) are placed seasonally (evenly distributed).
    The duration of each zero-value interval is controlled by `gap_duration_hours`.
    """

    def generate_timeseries(
        self,
        start_date: str,
        end_date: str,
        frequency: str = "30s",
        base_value: float = 100.0,
        slope: float = 2.0,  # Units per hour
        num_gaps: int = 3,
        gap_duration_hours: int = 1,  # Duration of each gap
        with_noise: bool = True,
        noise_level: float = 25.0,
        seed: int = 42,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Generate a monotonically increasing time series with seasonal zero-value intervals.

        Args:
            start_date: Start date string (YYYY-MM-DD HH:MM:SS).
            end_date: End date string (YYYY-MM-DD HH:MM:SS).
            frequency: Frequency string (e.g., '30s', '5m', '1h').
            base_value: The starting value of the time series.
            slope: The slope of the linear trend (units per hour).
            num_gaps: Number of seasonal zero-value intervals to introduce.
            gap_duration_hours: Duration (hours) of each zero-value interval.
            with_noise: Whether to add noise while preserving monotonicity.
            noise_level: Maximum noise level (always positive to maintain trend).
            seed: Random seed for reproducibility.

        Returns:
            DataFrame (TIMESTAMP, VALUE) and metadata dictionary.
        """
        np.random.seed(seed)
        random.seed(seed)

        start_ts = self.timestamp_to_unix(start_date)
        end_ts = self.timestamp_to_unix(end_date)
        interval_sec = self.parse_frequency(frequency)

        # 1. Generate potential timestamps and values
        potential_timestamps = np.arange(
            start_ts, end_ts + 1, interval_sec, dtype=int
        )
        num_potential_points = len(potential_timestamps)
        if num_potential_points == 0:
            return pd.DataFrame({"TIMESTAMP": [], "VALUE": []}), {
                "type": "trend_with_gaps",
                "params": {**locals(), "num_points": 0},
            }

        # Calculate time delta in hours for slope calculation
        time_delta_hours = (
            potential_timestamps - potential_timestamps[0]
        ) / 3600.0

        # Generate monotonically increasing base trend
        potential_values = base_value + slope * time_delta_hours

        # Add noise while preserving monotonicity
        if with_noise:
            # Generate positive-only noise to maintain monotonicity
            noise = np.random.uniform(0, noise_level, num_potential_points)

            # Ensure cumulative effect maintains monotonicity
            for i in range(1, num_potential_points):
                if potential_values[i] + noise[i] <= potential_values[i - 1]:
                    noise[i] = (
                        0  # Zero out noise that would break monotonicity
                    )

            potential_values += noise

        # 2. Determine seasonal start indices for zero-value intervals
        zero_start_indices = []
        if num_gaps > 0 and num_potential_points > 1:
            possible_indices = np.arange(1, num_potential_points - 1)
            if len(possible_indices) >= num_gaps:
                # Place intervals seasonally (evenly distributed)
                interval = max(1, len(possible_indices) // num_gaps)
                zero_start_indices = [
                    possible_indices[i * interval]
                    for i in range(num_gaps)
                    if i * interval < len(possible_indices)
                ]

        # Convert indices to timestamps and calculate end times
        zero_intervals = []
        gap_duration_sec = gap_duration_hours * 3600
        gap_info = []
        for idx in zero_start_indices:
            start_ts = potential_timestamps[idx]
            end_ts = start_ts + gap_duration_sec
            zero_intervals.append((start_ts, end_ts))
            gap_info.append(
                {  # Reuse gap_info for metadata
                    "zero_interval_start_timestamp": self.unix_to_datetime(
                        start_ts
                    ),
                    "zero_interval_end_timestamp": self.unix_to_datetime(
                        end_ts
                    ),
                    "zero_interval_duration_hours": gap_duration_hours,
                }
            )

        # 3. Build final timeseries, setting values to zero during intervals
        final_timestamps = []
        final_values = []
        for i, current_ts in enumerate(potential_timestamps):
            # Check if current timestamp falls within any zero interval
            is_in_zero_interval = False
            for start, end in zero_intervals:
                if start <= current_ts < end:
                    is_in_zero_interval = True
                    break

            # Decide the value to add
            value_to_add = 0.0 if is_in_zero_interval else potential_values[i]

            # Add the current point's timestamp and pre-calculated value
            final_timestamps.append(current_ts)
            final_values.append(value_to_add)

        df = pd.DataFrame(
            {"TIMESTAMP": final_timestamps, "VALUE": final_values}
        )

        metadata = {
            "type": "trend_with_gaps",
            "params": {
                "start_date": start_date,
                "end_date": end_date,
                "frequency": frequency,
                "base_value": base_value,
                "slope": slope,
                "num_gaps_requested": num_gaps,
                "num_zero_intervals_created": len(zero_intervals),
                "gap_duration_hours": gap_duration_hours,
                "with_noise": with_noise,
                "noise_level": noise_level,
                "seed": seed,
                "num_points_potential": num_potential_points,
                "num_points_actual": len(final_timestamps),
                "zero_intervals": gap_info,
            },
        }

        return df, metadata
