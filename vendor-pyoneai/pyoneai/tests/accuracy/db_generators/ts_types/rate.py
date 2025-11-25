#!/usr/bin/env python3
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd

from .base import BaseTimeseriesGenerator


class RateGenerator(BaseTimeseriesGenerator):
    """Generator for rate-based time series (e.g., bandwidth) with optional gaps.

    Rate metrics represent a value per unit time and can fluctuate,
    typically staying non-negative. Gaps simulate periods of no data.
    """

    def generate_timeseries(
        self,
        start_date: str,
        end_date: str,
        frequency: str = "30s",
        base_rate: float = 20.0,  # e.g., average Mbps
        with_noise: bool = True,
        noise_level: float = 20.0,  # Fluctuation around the base rate
        spike_probability: float = 0.05,  # Chance of a sudden spike
        spike_magnitude_factor: float = 3.0,  # How much larger spikes are
        num_resets: int = 1,
        reset_gap_hours: int = 1,  # Duration of each gap
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Generate a time series with rate-like behavior and optional gaps.


             spike_magnitude_factor: Multiplier for spike noise level.
             num_resets: Number of gaps to simulate.
             reset_gap_hours: Duration (hours) of each data gap.

        Returns:
            DataFrame (TIMESTAMP, VALUE) and metadata dictionary.
        """
        start_ts = self.timestamp_to_unix(start_date)
        end_ts = self.timestamp_to_unix(end_date)
        interval_sec = self.parse_frequency(frequency)

        # 1. Generate potential timestamps and rate values
        potential_timestamps = np.arange(
            start_ts, end_ts + 1, interval_sec, dtype=int
        )
        num_potential_points = len(potential_timestamps)
        if num_potential_points == 0:
            return pd.DataFrame({"TIMESTAMP": [], "VALUE": []}), {
                "type": "rate",
                "params": {**locals(), "num_points": 0},
            }

        potential_values = np.full(num_potential_points, base_rate)
        if with_noise:
            noise = np.random.normal(0, noise_level, num_potential_points)
            is_spike = np.random.rand(num_potential_points) < spike_probability
            spike_noise = np.random.normal(
                0, noise_level * spike_magnitude_factor, num_potential_points
            )
            noise[is_spike] = spike_noise[is_spike]
            potential_values += noise
        potential_values = np.maximum(
            0, potential_values
        )  # Ensure non-negative

        # 2. Determine indices where gaps should start
        reset_indices = set()
        if num_resets > 0 and num_potential_points > 1:
            possible_indices = np.arange(1, num_potential_points)
            if len(possible_indices) >= num_resets:
                chosen_indices = np.random.choice(
                    possible_indices, size=num_resets, replace=False
                )
                reset_indices = set(chosen_indices)

        # 3. Build final timeseries considering gaps
        final_timestamps = []
        final_values = []
        skip_until_ts = None
        gap_info = []

        for i, current_ts in enumerate(potential_timestamps):
            # Skip points during the gap
            if skip_until_ts and current_ts < skip_until_ts:
                continue

            # Check if we just finished a gap
            just_finished_gap = False
            if skip_until_ts and current_ts >= skip_until_ts:
                skip_until_ts = None
                just_finished_gap = True

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

            # Add the current point's timestamp and pre-calculated value
            final_timestamps.append(current_ts)
            value_to_add = potential_values[i]
            if just_finished_gap:
                value_to_add = 0.0  # Set value to 0 after gap
            final_values.append(value_to_add)

        df = pd.DataFrame(
            {"TIMESTAMP": final_timestamps, "VALUE": final_values}
        )

        metadata = {
            "type": "rate",
            "params": {
                "start_date": start_date,
                "end_date": end_date,
                "frequency": frequency,
                "base_rate": base_rate,
                "with_noise": with_noise,
                "noise_level": noise_level,
                "spike_probability": spike_probability,
                "spike_magnitude_factor": spike_magnitude_factor,
                "num_resets_requested": num_resets,
                "num_gaps_created": len(gap_info),
                "reset_gap_hours": reset_gap_hours,
                "num_points_potential": num_potential_points,
                "num_points_actual": len(final_timestamps),
                "gaps": gap_info,
            },
        }

        return df, metadata
