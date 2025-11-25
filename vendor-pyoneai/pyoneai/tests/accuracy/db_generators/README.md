# Synthetic Time Series Data Tools

## Generating Synthetic Databases

Generate synthetic time series data in SQLite databases using the `db_generator.py` script.

Accepted metric types: "sinusoidal", "constant", "counter", "peaks", "linear_trend", "step_change", "rate", "gauge_with_gaps", "trend_with_gaps"

```bash
# Basic usage
cd /opt/one-aiops/sdk
poetry run python ../sdk/pyoneai/tests/accuracy/db_generators/db_generator.py -i 100 -m cpu

# Generate with specific pattern
poetry run python ../sdk/pyoneai/tests/accuracy/db_generators/db_generator.py \
  -i 101 -m cpu --type sinusoidal -f 30m -s "2025-04-01 00:00:00" -e "2025-04-02 23:59:59" \
  -b 40 -d 15 -w 10

# Generate constant values (no noise)
poetry run python ../sdk/pyoneai/tests/accuracy/db_generators/db_generator.py \
  -i 102 -m memory --type constant -f 15m -s "2025-04-01" -e "2025-04-02" -b 2048 --no-noise

# Generate TS that has a linear trend but some gaps (value drop to 0)
petry run python ../sdk/pyoneai/tests/accuracy/db_generators/db_generator.py -i 17 -m gaugeLotGapsHighSlope --type trend_with_gaps --num-gaps 4 --gap-duration-hours 1

# Generate with peaks
poetry run python ../sdk/pyoneai/tests/accuracy/db_generators/db_generator.py \
  -i 103 -m cpu --type peaks --num-peaks 3 --min-peak-height 120 --max-peak-height 180 \
  --min-peak-width 5 --max-peak-width 15 -f 10m -s "2025-04-01" -e "2025-04-03" -b 50

# Generate multiple metrics in the same database
poetry run python ../sdk/pyoneai/tests/accuracy/db_generators/db_generator.py \
  -i 104 -m cpu --type sinusoidal -f 30m -s "2025-04-01" -e "2025-04-02" \
  --tables memory netrx nettx
```

### Key Parameters

- `-i, --id` - VM identifier (used in table names and filename)
- `-m, --metric` - Metric type (cpu, memory, netrx, nettx)
- `--type` - Pattern type (sinusoidal, constant, peaks, etc.)
- `-f, --frequency` - Sampling frequency (e.g., 15m, 1h)
- `-s, --start` - Start date
- `-e, --end` - End date 
- `-b, --base` - Base value
- `--tables` - Additional metrics to generate in the same database

## Visualizing the Data

Run the `plot_timeseries.py` script to plot ALL the values within each table in the specified database.

```bash
# Basic usage - plots all metrics in VM 101 database
cd /opt/one-aiops/sdk
poetry run python ../sdk/pyoneai/tests/accuracy/db_generators/plot_timeseries.py 101

# Plot multiple databases
poetry run python ../sdk/pyoneai/tests/accuracy/db_generators/plot_timeseries.py 101 102 103

# Specify custom output directory
poetry run python ../sdk/pyoneai/tests/accuracy/db_generators/plot_timeseries.py 101 --output-dir /path/to/save

# Show interactive plots without saving them
poetry run python ../sdk/pyoneai/tests/accuracy/db_generators/plot_timeseries.py 101 --display
```

Generated plot files are saved in `/opt/one-aiops/sdk/pyoneai/tests/accuracy/db_generators/plots/` by default. 