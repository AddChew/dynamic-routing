import os
import pytest


os.environ["env"] = "tests"


@pytest.fixture
def monkeypatch_users_dir(monkeypatch):
    """
    Monkeypatch users_dir.
    """
    monkeypatch.setattr(
        "src.projects.users_dir",
        os.path.join(os.path.abspath(os.path.dirname(os.path.abspath(__file__))), "tests", "users")
    )


@pytest.fixture
def monkeypatch_root(monkeypatch):
    """
    Monkeypatch root.
    """
    monkeypatch.setattr("src.main.root", "tests")