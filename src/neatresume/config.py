# SPDX-FileCopyrightText: 2025-present Ricardo Rivera <silkrad@ririlabs.com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import enum
from pathlib import Path

import pydantic
from reportlab.lib import pagesizes
from reportlab.lib.units import inch

from neatresume.resume import Resume
from neatresume.styles import Styles, Color


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
    primary: Color = pydantic.Field(default_factory=lambda: Color(hex_string="#003366"), validate_default=True, frozen=True)
    secondary: Color = pydantic.Field(default_factory=lambda: Color(hex_string="#666666"), validate_default=True, frozen=True)
    accent: Color = pydantic.Field(default_factory=lambda: Color(hex_string="#e1e8f0"), validate_default=True, frozen=True)


class Margins(pydantic.BaseModel):
    left: float = pydantic.Field(default=0.25 * inch, validate_default=True, frozen=True)
    right: float = pydantic.Field(default=0.25 * inch, validate_default=True, frozen=True)
    top: float = pydantic.Field(default=0.25 * inch, validate_default=True, frozen=True)
    bottom: float = pydantic.Field(default=0.25 * inch, validate_default=True, frozen=True)


class Options(pydantic.BaseModel):
    item_spacing: float = pydantic.Field(default=0.1 * inch, validate_default=True, frozen=True)
    section_spacing: float = pydantic.Field(default=0.3 * inch, validate_default=True, frozen=True)
    column_gap: float = pydantic.Field(default=0.2 * inch, validate_default=True, frozen=True)
    column_split: float = pydantic.Field(default=0.30, validate_default=True, frozen=True)


class Page(pydantic.BaseModel):
    colors: Colors = pydantic.Field(default_factory=Colors, validate_default=True, frozen=True)
    margins: Margins = pydantic.Field(default_factory=Margins, validate_default=True, frozen=True)
    paper: PageSize = pydantic.Field(default=PageSize.LETTER, validate_default=True, frozen=True)
    options: Options = pydantic.Field(default_factory=Options, validate_default=True, frozen=True)

    @pydantic.computed_field
    @property
    def width(self) -> float:
        return self.paper.size[0] - self.margins.left - self.margins.right

    @pydantic.computed_field
    @property
    def height(self) -> float:
        return self.paper.size[1] - self.margins.top - self.margins.bottom

    @pydantic.computed_field
    @property
    def height_full(self) -> float:
        return self.paper.size[1]

    @pydantic.computed_field
    @property
    def column_left_width(self) -> float:
        return self.width * self.options.column_split

    @pydantic.computed_field
    @property
    def column_right_width(self) -> float:
        return self.width * (1 - self.options.column_split)


class Config(pydantic.BaseModel):
    file: Path = pydantic.Field(frozen=True)
    resume: Resume = pydantic.Field(frozen=True)

    page: Page = pydantic.Field(default_factory=Page, validate_default=True, frozen=True)
    styles: Styles = pydantic.Field(default_factory=Styles, validate_default=True, frozen=True)
