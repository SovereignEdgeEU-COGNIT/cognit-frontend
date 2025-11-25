import argparse
import importlib
import importlib.util
import sys
from datetime import datetime, timezone
from unittest.mock import MagicMock, mock_open

import numpy as np
import pytest

from pyoneai.ml import ArtifactManager
from pyoneai.tests.performance.config import (
    DATA_DIR,
    FORECAST_CONF_FILE,
    VM_IDS,
)
from pyoneai.tests.performance.utils import (
    measure_multiple_executions,
    save_result,
)


def get_forecast_conf_content():
    return FORECAST_CONF_FILE.expanduser().absolute().read_text()


def load_prediction_script():
    module_name = "prediction"
    path = importlib.resources.files("pyoneai").joinpath(
        "..", "..", "monitoring", "prediction.py"
    )
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class TestMonitoringScript:

    @pytest.fixture(autouse=True)
    def setup(self, mocker, prediction_model, pytestconfig):
        self.prediction_model = prediction_model
        self.trials = pytestconfig.getoption("trials")
        self.prediction = load_prediction_script()
        self.open_mock = mocker.patch.object(
            self.prediction,
            "open",
            mock_open(read_data=get_forecast_conf_content()),
        )
        mock_artifact = MagicMock(spec=ArtifactManager)
        mock_artifact.load.return_value = prediction_model
        self.open_mock = mocker.patch.object(
            self.prediction, "ArtifactManager", return_value=mock_artifact
        )

        self.type = "virtualmachine"
        # NOTE: patch STDOUT to avoid long printed messages coming from script
        mocker.patch.object(self.prediction, "print")

    @pytest.fixture(scope="session")
    def exp_dir(self):
        yield datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")

    @pytest.mark.parametrize("vm_id", VM_IDS)
    def test_run_shortterm(self, exp_dir, mocker, vm_id):
        self.arg_mock = mocker.patch(
            "argparse.ArgumentParser.parse_args",
            return_value=argparse.Namespace(
                entity={
                    "type": self.type,
                    "id": vm_id,
                    "uuid": 0,
                    "db_dir": DATA_DIR,
                },
                pythonpath=".",
            ),
        )
        times = measure_multiple_executions(self.prediction.main, self.trials)
        avg_time = np.mean(times)
        std_time = np.std(times)
        save_result(
            exp_dir=exp_dir,
            result={
                "predictiom_model": type(self.prediction_model).__name__,
                "vm_id": vm_id,
                "avg_time": avg_time,
                "std_time": std_time,
            },
        )
        print(
            f"Average execution time out of {self.trials} "
            f"for {vm_id} virtual machine equals to "
            f"{avg_time:.2f} ± {std_time:.2f} [sec]."
        )
