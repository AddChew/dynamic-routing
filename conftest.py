import os
import pytest


os.environ["env"] = "tests"


@pytest.fixture
def monkeypatch_users_dir(monkeypatch):
    """
    Monkeypatch USERS_DIR.
    """
    monkeypatch.setattr(
        "src.projects.USERS_DIR",
        os.path.join(os.path.abspath(os.path.dirname(os.path.abspath(__file__))), "tests", "users")
    )