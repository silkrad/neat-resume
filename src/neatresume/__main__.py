# SPDX-FileCopyrightText: 2025-present Ricardo Rivera <silkrad@ririlabs.com>
#
# SPDX-License-Identifier: Apache-2.0

import json
from pathlib import Path

from neatresume.config import Config
from neatresume.generator import Generator


def main():
    config = _load_config(Path("tests/examples/alex_chen_resume.json"))
    Generator(config=config).generate()


def _load_config(json_path: Path) -> Config:
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")
    with json_path.open("r", encoding="utf-8") as f:
        json_data = json.load(f)
    return Config.model_validate(json_data)


if __name__ == "__main__":
    main()
