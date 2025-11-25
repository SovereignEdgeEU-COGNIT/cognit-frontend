import importlib

PERFORMANCE_DIR = importlib.resources.files("pyoneai").joinpath(
    "tests", "performance"
)
FORECAST_CONF_FILE = PERFORMANCE_DIR / "resources" / "forecast.conf"
DATA_DIR = PERFORMANCE_DIR / "resources" / "data"
REPORT_DIR = PERFORMANCE_DIR / "report"

VM_IDS = DATA_DIR.glob("*.db")
VM_IDS = [vm_id.stem for vm_id in VM_IDS]
