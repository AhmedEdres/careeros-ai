"""Shared pytest fixtures.

Ensures tests never write the application data file into the repository.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(autouse=True)
def isolated_data_file(tmp_path, monkeypatch):
    monkeypatch.setenv("CAREEROS_DATA_FILE", str(tmp_path / "applied_jobs.json"))
    yield
