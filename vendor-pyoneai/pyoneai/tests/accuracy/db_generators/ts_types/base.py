#!/usr/bin/env python3
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Tuple

import pandas as pd


class BaseTimeseriesGenerator(ABC):
    """Base class for all time series generators.

    This abstract class defines the interface that all time series generators must implement.
    Each subclass should implement the generate_timeseries method to create specific patterns.
    """

    @abstractmethod
    def generate_timeseries(
        self, start_date: str, end_date: str, frequency: str, **kwargs
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Generate a time series with the specific pattern.

        Parameters
        ----------
        start_date : str
            Start date in format 'YYYY-MM-DD HH:MM:SS'
        end_date : str
            End date in format 'YYYY-MM-DD HH:MM:SS'
        frequency : str
            Frequency of the time series (e.g., '30s', '5m', '1h', '1d')
        **kwargs : dict
            Additional parameters specific to each generator type

        Returns
        -------
        Tuple[pd.DataFrame, Dict[str, Any]]
            DataFrame with TIMESTAMP and VALUE columns, and metadata dictionary
        """
        pass

    @staticmethod
    def timestamp_to_unix(dt_str: str) -> int:
        """Convert datetime string to Unix timestamp."""
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        return int(dt.timestamp())

    @staticmethod
    def unix_to_datetime(unix_time: int) -> str:
        """Convert Unix timestamp to datetime string."""
        return datetime.fromtimestamp(unix_time).strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def parse_frequency(frequency: str) -> int:
        """Parse frequency string (e.g., '30s', '5m', '1h') to seconds."""
        freq_value = int(frequency[:-1])
        freq_unit = frequency[-1]

        seconds_per_unit = {
            "s": 1,
            "m": 60,
            "h": 3600,
            "d": 86400,
            "M": 60 * 60 * 24 * 30,
            "y": 60 * 60 * 24 * 365,
        }

        if freq_unit not in seconds_per_unit:
            raise ValueError(
                f"Unsupported frequency unit: {freq_unit}. Use 's', 'm', 'h', 'd', 'M', or 'y'."
            )

        return freq_value * seconds_per_unit[freq_unit]
