#!/usr/bin/env python3
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd

from .base import BaseTimeseriesGenerator


class GaugeWithGapsGenerator(BaseTimeseriesGenerator):
    """Generator for Gauge time series with simulated gaps (resets).

    Simulates a gauge metric where the value fluctuates but resets to 0
    after a data gap, mimicking events like VM restarts.
    """

    def generate_timeseries(
        self,
        start_date: str,
        end_date: str,
        frequency: str = "30s",
        base_value: float = 50.0,
        with_noise: bool = True,
        noise_level: float = 10.0,
        num_resets: int = 1,
        reset_gap_hours: int = 2,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Generate a time series with gauge behavior and gaps.

        Parameters
        ----------
        start_date : str
            Start date in format 'YYYY-MM-DD HH:MM:SS'
        end_date : str
            End date in format 'YYYY-MM-DD HH:MM:SS'
        frequency : str
            Frequency of the time series (e.g., '30s', '5m', '1h')
        base_value : float
            Base value around which the gauge fluctuates.
        with_noise : bool
            Whether to add random noise/fluctuations.
        noise_level : float
            Standard deviation of the noise.
        num_resets : int
            Number of gaps (resets) to simulate.
        reset_gap_hours : int
            Duration (in hours) of each data gap after a reset.

        Returns
        -------
        Tuple[pd.DataFrame, Dict[str, Any]]
            DataFrame with TIMESTAMP and VALUE columns, and metadata dictionary
        """
        start_ts = self.timestamp_to_unix(start_date)
        end_ts = self.timestamp_to_unix(end_date)
        interval_sec = self.parse_frequency(frequency)

        # Generate potential timestamps and values if no gaps existed
        potential_timestamps = np.arange(
            start_ts, end_ts + 1, interval_sec, dtype=int
        )
        num_potential_points = len(potential_timestamps)
        if num_potential_points == 0:
            return pd.DataFrame({"TIMESTAMP": [], "VALUE": []}), {
                "type": "gauge_with_gaps",
                "params": {**locals(), "num_points": 0},
            }

        potential_values = np.full(num_potential_points, base_value)
        if with_noise:
            potential_values += np.random.normal(
                0, noise_level, num_potential_points
            )

        # Determine indices where resets (gaps) should start
        reset_indices = set()
        if num_resets > 0 and num_potential_points > 1:
            possible_indices = np.arange(1, num_potential_points)
            if len(possible_indices) >= num_resets:
                chosen_indices = np.random.choice(
                    possible_indices, size=num_resets, replace=False
                )
                reset_indices = set(chosen_indices)

        # Build final timeseries considering gaps and resets
        final_timestamps = []
        final_values = []
        skip_until_ts = None
        gap_info = []
        is_after_gap = False

        for i, current_ts in enumerate(potential_timestamps):
            # Skip points during the gap
            if skip_until_ts and current_ts < skip_until_ts:
                continue

            # Check if we just finished a gap
            if skip_until_ts and current_ts >= skip_until_ts:
                skip_until_ts = None
                is_after_gap = True

            # Check if this point triggers a gap
            if i in reset_indices:
                gap_start_time = self.unix_to_datetime(current_ts)
                skip_until_ts = current_ts + reset_gap_hours * 3600
                gap_end_time = self.unix_to_datetime(skip_until_ts)
                gap_info.append(
                    {
                        "gap_start_timestamp": gap_start_time,
                        "gap_end_timestamp": gap_end_time,
                        "gap_duration_hours": reset_gap_hours,
                    }
                )
                continue  # Skip this point, start the gap

            # Determine the value for the current point
            current_value = 0.0 if is_after_gap else potential_values[i]
            is_after_gap = False  # Reset flag after using it

            final_timestamps.append(current_ts)
            final_values.append(current_value)

        df = pd.DataFrame(
            {"TIMESTAMP": final_timestamps, "VALUE": final_values}
        )

        metadata = {
            "type": "gauge_with_gaps",
            "params": {
                "start_date": start_date,
                "end_date": end_date,
                "frequency": frequency,
                "base_value": base_value,
                "with_noise": with_noise,
                "noise_level": noise_level,
                "num_resets_requested": num_resets,
                "num_gaps_created": len(gap_info),
                "reset_gap_hours": reset_gap_hours,
                "num_points_potential": num_potential_points,
                "num_points_actual": len(final_timestamps),
                "gaps": gap_info,
            },
        }

        return df, metadata
