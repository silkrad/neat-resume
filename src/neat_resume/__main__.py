# SPDX-FileCopyrightText: 2025-present Ricardo Rivera <silkrad@ririlabs.com>
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
import argparse

from neat_resume.config import Config
from neat_resume.generator import Generator


def main(argv: list[str] | None = None) -> None:
    """CLI entrypoint.

    Accepts a --config / -c argument pointing to a JSON file describing the resume.
    If not provided, falls back to the example in tests/examples.
    """
    argv = list(argv) if argv is not None else None
    parser = argparse.ArgumentParser(description="Generate a resume from a JSON config file")
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        help="Path to resume config JSON file",
        required=True,
    )

    args = parser.parse_args(argv)

    config_path: Path = args.config
    if not config_path.exists():
        parser.error(f"config file not found: {config_path}")

    resume_config = _load_config(config_path)
    Generator(config=resume_config).generate()


def _load_config(json_path: Path) -> Config:
    with json_path.open(mode="r", encoding="utf-8") as resume_file:
        resume_config = Config.model_validate_json(resume_file.read())
        return resume_config


if __name__ == "__main__":
    main()
