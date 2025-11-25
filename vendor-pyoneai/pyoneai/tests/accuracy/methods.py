from pyoneai.ml.model_config import ModelConfig


def get_persistence():
    from pyoneai.ml.persistence_prediction_model import (
        PersistencePredictionModel,
    )

    return PersistencePredictionModel(
        ModelConfig(
            model_class="pyoneai.ml.PersistencePredictionModel",
            sequence_length=30,
            compute_ci=False,
            hyper_params={"context_length": 200},
        )
    )


def get_arima():
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
                "order": (1, 1, 1),
            },
        )
    )


def get_hgbt():
    from pyoneai.ml.hgbt_prediction_model import HgbtPredictionModel

    return HgbtPredictionModel(
        ModelConfig(
            model_class="sklearn.ensemble.HistGradientBoostingRegressor",
            sequence_length=30,
            compute_ci=False,
            training_params={"context_length": 200, "max_iter": 50},
        )
    )


def get_fourier():
    from pyoneai.ml.fourier_prediction_model import FourierPredictionModel

    return FourierPredictionModel(
        ModelConfig(
            model_class="pyoneai.ml.FourierPredictionModel",
            sequence_length=30,
            compute_ci=False,
            hyper_params={"quick_fit": False},
        )
    )


def get_prophet():
    from pyoneai.ml.prophet_prediction_model import ProphetPredictionModel

    return ProphetPredictionModel(
        ModelConfig(
            model_class="pyoneai.ml.ProphetPredictionModel",
            sequence_length=30,
            compute_ci=False,
            hyper_params={},
        )
    )


def get_linear():
    from pyoneai.ml.linear_prediction_model import LinearPredictionModel

    return LinearPredictionModel(
        ModelConfig(
            model_class="pyoneai.ml.LinearPredictionModel",
            sequence_length=30,
            compute_ci=False,
            hyper_params={},
        )
    )


def get_methods(methods: list[str]) -> list:
    method_map = {
        "persistence": get_persistence,
        "arima": get_arima,
        "hgbt": get_hgbt,
        "fourier": get_fourier,
        "prophet": get_prophet,
        "linear": get_linear,
    }

    selected_methods = []
    for method in methods:
        if method in method_map:
            selected_methods.append(method_map[method]())
        else:
            raise ValueError(f"Unknown method: {method}")

    return selected_methods
