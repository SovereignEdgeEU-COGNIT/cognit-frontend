# Accuracy tests
The accuracy test facility has the following structure:

| Directory | What does it contain? | 
| --------- | --------------------- |
| `db_generators` | Definition of time series generators (e.g. sinusoidal) |
| `resources` | Directory where database file will be created |
| `report` | Directory with accuracy reports grouped by horizon, metric name, and ML method |
| `scripts`| Contains scripts to create database or run example short-term or long-term forecast accuracy tests |
| `utils` | Contains utilities, e.g. measuring time or taking date-range from DB | 

## 1. Creating database
To create a database with predefined characteristics, run

```bash
python3 db_generators/generate_db.py
```

It will create a `data.db` file under `resources` directory in accuracy tests.

> [!IMPORTANT]\
> Do not move that file, it is automatically discovered by accuracy tests.

## 2. (Optional) Adding new time series (characteristic)

To add new time series, you need to modify script `db_generators/generate_db.py` by extending `TIMESERIES` dictionary with the new characteristic definition. Then, run the `generate_db.py` script.

> [!IMPORTANT]\
> To use newly created timeseries in accuracy tests, you need to modify `config.py` module.
> Add correpsonding `MetricAttributes` definition to the proper dictionary: `BASIC_METRICS`, `SHORT_TERM_METRICS`, or `LONG_TERM_METRICS`.

## 3. Running accuracy tests
To run accuract test, you just need to call `accuracy_test.py` script with proper arguments.


| Argument | Shortname | Meaning  | Example
| ---------| -------- | --------- | ------- |
| `--horizon` | `-H` | Forecast horizon | `-H 15m` |
| `--method` | `-m` | ML method to be used | `-m linear -m fourier`|
|`--freq` | `-f`| Resolution of resulting data (can be used for resampling) | `-f 1h`|
|`--lookback`|`-l`| Lookback for the ML method (historical context) | `-l 48h`|
|`--step` |`-s`| For moving window test, how big the step should be, default to `1` | `-s 100`|
|`--no_seasonality_metrics`|`-nsm`|If time series with no seasonality should be used (defined in `NO_SEASONALITY_METRICS` in `config.py`) |
|`--hourly_metrics`|`-hm`|If time series with hour-related seasonality pattern (defined in `HOURLY_SEASONALITY_METRICS` in `config.py`) |
|`--daily_metrics`|`-hm`|If time series with daily-related seasonality pattern (defined in `DAILY_SEASONALITY_METRICS` in `config.py`) |
|`--weekly_metrics`|`-wm`|If time series with weekly-related seasonality pattern (defined in `WEEKLY_SEASONALITY_METRICS` in `config.py`) |
|`--monthly_metrics`|`-hm`|If time series with monthly-related seasonality pattern (defined in `MONTHLY_SEASONALITY_METRICS` in `config.py`) |
|`--plot_all`|`-pa` | If all windows plots should be saved | `--plot_all`|

> [!WARNING]\
> Running tests with `plot_all` option can produce excessive number of plots and can increase time of accuracy tests.


> [!NOTE]\
> Supported time units are following (`s` - second, `m` - minute, `h` - hour, `d` - day, `w` - week, `M` - approximate month)


An example of short term accuracy test can be reached by running:

```bash
python3 accuracy_test.py \
    --horizon "10m" \
    --freq "30s" \
    --lookback "120m" \
    --method fourier \
    --method linear \
    --step 100
    --no_seasonality_metrics \
    --daily_metrics \
    --weekly_metrics \
    --plot_all
```

or by adjusting and running `run_shortterm_forecast.sh`.

> [!NOTE]\
> All resulting data, including CSV files with quality metrics for moving window evaluation will be saved under the `report` directory.