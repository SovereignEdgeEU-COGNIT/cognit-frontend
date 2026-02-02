from pyoneai.ml.model_config import ModelConfig

_AVAILABLE_ML_METHODS_NAMES = ["arima", "hgbt", "fourier", "prophet"]


def pytest_addoption(parser):
    for ml in _AVAILABLE_ML_METHODS_NAMES:
        parser.addoption(
            f"--{ml}",
            action="store_true",
            default=False,
            help="Run performance tests for %s" % ml,
        )

    parser.addoption(
        "--trials",
        default=30,
        type=int,
        help="Number of trials to run for each test",
    )


def _get_arima():
    from pyoneai.ml.arima_prediction_model import ArimaPredictionModel

    return ArimaPredictionModel(
        ModelConfig(
            model_class="statsmodels.tsa.arima.model.ARIMA",
            sequence_length=30,
            compute_ci=False,
            hyper_params={
                "enforce_stationarity": True,
                "enforce_invertibility": True,
                "concentrate_scale": False,
                "trend_offset": 1,
            },
        )
    )


def _get_hgbt():
    from pyoneai.ml.hgbt_prediction_model import HgbtPredictionModel

    return HgbtPredictionModel(
        ModelConfig(
            model_class="sklearn.ensemble.HistGradientBoostingRegressor",
            sequence_length=30,
            compute_ci=False,
            training_params={"context_length": 200, "max_iter": 50},
        )
    )


def _get_fourier():
    from pyoneai.ml.fourier_prediction_model import FourierPredictionModel

    return FourierPredictionModel(
        ModelConfig(
            model_class="pyoneai.ml.FourierPredictionModel",
            sequence_length=30,
            compute_ci=False,
            hyper_params={"nbr_freqs_to_keep": 40},
        )
    )


def _get_prophet():
    from pyoneai.ml.prophet_prediction_model import ProphetPredictionModel

    return ProphetPredictionModel(
        ModelConfig(
            model_class="pyoneai.ml.ProphetPredictionModel",
            sequence_length=30,
            compute_ci=False,
        )
    )


def pytest_generate_tests(metafunc):
    if "prediction_model" in metafunc.fixturenames:
        ml_model = []
        if metafunc.config.getoption("fourier"):
            ml_model.append(_get_fourier())
        if metafunc.config.getoption("arima"):
            ml_model.append(_get_arima())
        if metafunc.config.getoption("hgbt"):
            ml_model.append(_get_hgbt())
        if metafunc.config.getoption("prophet"):
            ml_model.append(_get_prophet())
        if not ml_model:
            ml_model = [
                _get_arima(),
                _get_fourier(),
                _get_hgbt(),
                _get_prophet(),
            ]
        metafunc.parametrize("prediction_model", ml_model)
