import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "seed" / "seed.py"

spec = importlib.util.spec_from_file_location("seed_module", MODULE_PATH)
seed_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seed_module)


def test_format_display_name_title_cases_common_names():
    assert seed_module._format_display_name("semmat tech") == "Semmat Tech"


def test_format_display_name_preserves_acronyms():
    assert seed_module._format_display_name("HAE Consulting") == "HAE Consulting"


def test_normalize_placeholder_service_title_strips_placeholder_suffix():
    assert seed_module._normalize_placeholder_service_title(
        "United Ecosystem Placeholder Service",
        "United Ecosystem",
    ) == "United Ecosystem"
