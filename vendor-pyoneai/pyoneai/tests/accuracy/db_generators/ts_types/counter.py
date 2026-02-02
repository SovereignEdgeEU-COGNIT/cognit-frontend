#!/usr/bin/env python3
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd

from .base import BaseTimeseriesGenerator


class CounterGenerator(BaseTimeseriesGenerator):
    """Generator for Prometheus-like counter time series.

    A counter is a cumulative metric that represents a single monotonically
    increasing counter whose value can only increase or be reset to zero.
    """

    def generate_timeseries(
        self,
        start_date: str,
        end_date: str,
        frequency: str = "30s",
        base_value: float = 5.0,
        with_noise: bool = True,
        noise_level: float = 1.0,
        num_resets: int = 1,
        reset_gap_hours: int = 6,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Generate a time series with counter-like behavior.

        Parameters
        ----------
        start_date : str
            Start date in format 'YYYY-MM-DD HH:MM:SS'
        end_date : str
            End date in format 'YYYY-MM-DD HH:MM:SS'
        frequency : str
            Frequency of the time series (e.g., '30s', '5m', '1h', '1d')
        base_value : float
            Base increment rate per time unit
        with_noise : bool
            Whether to add noise to the increment rate
        noise_level : float
            Standard deviation of noise applied to the rate
        num_resets : int
            Number of counter resets to simulate
        reset_gap_hours : int
            Hours to pause data collection after a reset

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

        # Create full continuous timestamp range
        continuous_timestamps = np.arange(
            start_timestamp,
            end_timestamp + 1,
            interval_seconds,
            dtype=int,
        )

        # Initialize arrays for actual timestamps and values
        timestamps = []
        values = []
        current_value = 0.0

        # Track reset information
        reset_info = []

        # Generate reset points if needed
        reset_indices = []
        if (
            num_resets > 0 and len(continuous_timestamps) > 1
        ):  # Cannot have resets if only 0 or 1 point
            segment_size = max(
                1, len(continuous_timestamps) // (num_resets + 1)
            )
            last_reset_idx = -1

            for i in range(num_resets):
                # Define the segment boundaries for the i-th reset (0-indexed loop)
                # Segments conceptually start after the previous segment ends
                segment_start = i * segment_size
                segment_end = (
                    i + 1
                ) * segment_size - 1  # -1 because index is inclusive

                # Determine the earliest possible index for this reset
                # Must be after the last reset and cannot be the very first point (index 0)
                lower_bound = max(segment_start, last_reset_idx + 1, 1)

                # Ensure the potential range is valid
                if lower_bound <= segment_end:
                    # Choose a random index within the allowed range for this segment
                    reset_idx = np.random.randint(lower_bound, segment_end + 1)

                    # Store the index if it's valid and update the last reset position
                    if (
                        reset_idx > last_reset_idx
                    ):  # Should always be true given lower_bound logic, but safe check
                        reset_indices.append(reset_idx)
                        last_reset_idx = reset_idx
                    # else: If lower_bound > segment_end, a reset cannot be placed
                    # in this segment without violating order or boundaries.
                    # This can happen if num_resets is high relative to total_points.
                    # We simply skip adding a reset in this case.

        # Process each timestamp in the continuous range
        skip_until_timestamp = None

        for i, timestamp in enumerate(continuous_timestamps):
            # Skip points during downtime after a reset
            if skip_until_timestamp and timestamp < skip_until_timestamp:
                continue

            # Check if this is a reset point
            if i in reset_indices:
                # Record reset information
                reset_info.append(
                    {
                        "timestamp": self.unix_to_datetime(timestamp),
                        "value_before_reset": current_value,
                    }
                )

                # Reset the counter to zero
                current_value = 0.0

                # Calculate next timestamp after gap
                skip_until_timestamp = timestamp + reset_gap_hours * 3600
                continue

            # Calculate increment for this period
            increment = base_value

            # Add noise if requested
            if with_noise:
                increment += np.random.normal(0, noise_level)
                increment = max(0, increment)  # Ensure no negative increments

            # Add to the counter
            current_value += increment

            timestamps.append(timestamp)
            values.append(current_value)

        # Create DataFrame
        df = pd.DataFrame({"TIMESTAMP": timestamps, "VALUE": values})

        # Create metadata
        metadata = {
            "type": "counter",
            "params": {
                "start_date": start_date,
                "end_date": end_date,
                "base_value": base_value,
                "with_noise": with_noise,
                "noise_level": noise_level,
                "num_resets": num_resets,
                "reset_gap_hours": reset_gap_hours,
                "num_points": len(timestamps),
                "frequency": frequency,
                "resets": reset_info,
            },
        }

        return df, metadata
