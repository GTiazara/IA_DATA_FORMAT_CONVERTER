from pathlib import Path

import pytest


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    path = tmp_path / "data.csv"
    path.write_text("id,score,label\n1,0.5,cat\n2,1.25,dog\n3,,bird\n", encoding="utf-8")
    return path
