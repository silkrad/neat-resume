# SPDX-FileCopyrightText: 2025-present Ricardo Rivera <silkrad@ririlabs.com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import enum
from pathlib import Path

import pydantic
from reportlab.lib import pagesizes
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.colors import Color

from neatresume.resume import Resume
from neatresume.styles import Styles


class PageSize(enum.StrEnum):
    A3 = enum.auto()
    A4 = enum.auto()
    A5 = enum.auto()
    LEGAL = enum.auto()
    LETTER = enum.auto()

    @property
    def page_size(self) -> tuple[float, float]:
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
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    primary: Color = pydantic.Field(default=colors.HexColor("#003366"), frozen=True)
    secondary: Color = pydantic.Field(default=colors.HexColor("#666666"), frozen=True)
    accent: Color = pydantic.Field(default=colors.HexColor("#e1e8f0"), frozen=True)


class Margins(pydantic.BaseModel):
    left: float = pydantic.Field(default=0.25 * inch, frozen=True)
    right: float = pydantic.Field(default=0.25 * inch, frozen=True)
    top: float = pydantic.Field(default=0.25 * inch, frozen=True)
    bottom: float = pydantic.Field(default=0.25 * inch, frozen=True)


class Options(pydantic.BaseModel):
    item_spacing: float = pydantic.Field(default=0.1 * inch, frozen=True)
    section_spacing: float = pydantic.Field(default=0.3 * inch, frozen=True)
    column_gap: float = pydantic.Field(default=0.2 * inch, frozen=True)
    column_split: float = pydantic.Field(default=0.34, frozen=True)


class Page(pydantic.BaseModel):
    colors: Colors = pydantic.Field(default_factory=Colors, frozen=True)
    margins: Margins = pydantic.Field(default_factory=Margins, frozen=True)
    size: PageSize = pydantic.Field(default=PageSize.LETTER, frozen=True)
    options: Options = pydantic.Field(default_factory=Options, frozen=True)

    @pydantic.computed_field
    @property
    def width(self) -> float:
        return self.size.page_size[0]

    @pydantic.computed_field
    @property
    def height(self) -> float:
        return self.size.page_size[1]

    @pydantic.computed_field
    @property
    def column_left_width(self) -> float:
        return self.width * self.options.column_split

    @pydantic.computed_field
    @property
    def column_right_width(self) -> float:
        return self.width - self.column_left_width


class Config(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    file: Path = pydantic.Field(frozen=True)
    page: Page = pydantic.Field(default_factory=Page, frozen=True)
    resume: Resume = pydantic.Field(frozen=True)
    styles: Styles = pydantic.Field(default_factory=Styles, frozen=True)
