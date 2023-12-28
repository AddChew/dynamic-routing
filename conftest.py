import os
import pytest


os.environ["db_url"] = "sqlite://:memory:"
os.environ["root_module"] = "tests"


@pytest.fixture
def monkeypatch_users_dir(monkeypatch):
    """
    Monkeypatch USERS_DIR.
    """
    monkeypatch.setattr(
        "src.projects.USERS_DIR",
        os.path.join(os.path.abspath(os.path.dirname(os.path.abspath(__file__))), "tests", "users")
    )