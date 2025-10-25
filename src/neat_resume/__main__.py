# SPDX-FileCopyrightText: 2025-present Ricardo Rivera <silkrad@ririlabs.com>
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from neat_resume.config import Config
from neat_resume.generator import Generator


def main():
    resume_config = _load_config(Path("tests/examples/sarah_johnson_resume.json"))
    Generator(config=resume_config).generate()


def _load_config(json_path: Path) -> Config:
    with json_path.open(mode="r", encoding="utf-8") as resume_file:
        resume_config = Config.model_validate_json(resume_file.read())
        return resume_config


if __name__ == "__main__":
    main()
