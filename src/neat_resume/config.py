# SPDX-FileCopyrightText: 2025-present Ricardo Rivera <silkrad@ririlabs.com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import enum
from datetime import date
from pathlib import Path

import pydantic
from reportlab.lib import pagesizes
from reportlab.lib.units import inch

from neat_resume.resume import Resume
from neat_resume.styles import Styles, Color


class PageSize(enum.StrEnum):
    A3 = enum.auto()
    A4 = enum.auto()
    A5 = enum.auto()
    LEGAL = enum.auto()
    LETTER = enum.auto()

    @property
    def size(self) -> tuple[float, float]:
        match self:
            case PageSize.A3:
                return pagesizes.A3
            case PageSize.A4:
                return pagesizes.A4
            case PageSize.A5:
                return pagesizes.A5
            case PageSize.LEGAL:
                return pagesizes.LEGAL
            case PageSize.LETTER:
                return pagesizes.LETTER
            case _:
                raise ValueError("unsupported page size")


class Colors(pydantic.BaseModel):
    frame_left: Color = pydantic.Field(default_factory=lambda: Color(hex_string="#e1e8f0"), validate_default=True, frozen=True)
    frame_right: Color = pydantic.Field(default_factory=lambda: Color(hex_string="#ffffff"), validate_default=True, frozen=True)


class Margins(pydantic.BaseModel):
    left: float = pydantic.Field(default=0.25 * inch, validate_default=True, frozen=True)
    right: float = pydantic.Field(default=0.25 * inch, validate_default=True, frozen=True)
    top: float = pydantic.Field(default=0.25 * inch, validate_default=True, frozen=True)
    bottom: float = pydantic.Field(default=0.25 * inch, validate_default=True, frozen=True)


class Options(pydantic.BaseModel):
    column_gap: float = pydantic.Field(default=0.1 * inch, validate_default=True, frozen=True)
    indent_spacing: float = pydantic.Field(default=0.15 * inch, validate_default=True, frozen=True)
    item_spacing: float = pydantic.Field(default=0.1 * inch, validate_default=True, frozen=True)
    section_spacing: float = pydantic.Field(default=0.3 * inch, validate_default=True, frozen=True)
    sidebar_size: float = pydantic.Field(default=0.35, validate_default=True, frozen=True)


class Page(pydantic.BaseModel):
    colors: Colors = pydantic.Field(default_factory=Colors, validate_default=True, frozen=True)
    margins: Margins = pydantic.Field(default_factory=Margins, validate_default=True, frozen=True)
    paper: PageSize = pydantic.Field(default=PageSize.LETTER, validate_default=True, frozen=True)
    options: Options = pydantic.Field(default_factory=Options, validate_default=True, frozen=True)

    @property
    def content_width(self) -> float:
        return self.paper.size[0] - self.margins.left - self.margins.right

    @property
    def content_height(self) -> float:
        return self.paper.size[1] - self.margins.top - self.margins.bottom

    @property
    def page_height(self) -> float:
        return self.paper.size[1]

    @property
    def page_width(self) -> float:
        return self.paper.size[0]

    @property
    def main_width(self) -> float:
        return self.content_width * (1 - self.options.sidebar_size)

    @property
    def sidebar_width(self) -> float:
        return self.content_width * self.options.sidebar_size


class Config(pydantic.BaseModel):
    resume: Resume = pydantic.Field(frozen=True)

    file: Path = pydantic.Field(default_factory=Path, validate_default=True)
    page: Page = pydantic.Field(default_factory=Page, validate_default=True, frozen=True)
    styles: Styles = pydantic.Field(default_factory=Styles, validate_default=True, frozen=True)

    @pydantic.model_validator(mode="after")
    def generate_filename(self) -> Config:
        """Generate filename if not provided, based on candidate name and current date."""
        if self.file == Path():
            candidate_name = self.resume.candidate.name.lower().replace(" ", "_")
            current_date = date.today().strftime("%Y-%m-%d")
            self.file = Path(f"{candidate_name}_resume_{current_date}.pdf")
        return self
