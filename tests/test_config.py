from __future__ import annotations

from contextpack.config import load_config, write_default_config


def test_write_and_load_config(sample_repo):
    path = write_default_config(sample_repo)
    assert path.exists()
    config = load_config(sample_repo)
    assert config.max_file_size_kb == 128
