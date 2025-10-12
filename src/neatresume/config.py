# SPDX-FileCopyrightText: 2025-present Ricardo Rivera <silkrad@ririlabs.com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import enum
from pathlib import Path
from typing import ClassVar

import pydantic
from reportlab.lib import pagesizes
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.colors import Color
from reportlab.lib.styles import ParagraphStyle, StyleSheet1

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


class Defaults:
    COLOR_ACCENT: ClassVar[Color] = colors.HexColor("#e1e8f0")
    COLOR_PRIMARY: ClassVar[Color] = colors.HexColor("#003366")
    COLOR_SECONDARY: ClassVar[Color] = colors.HexColor("#666666")
    COLUMN_GAP: ClassVar[float] = 0.2 * inch
    COLUMN_SPLIT: ClassVar[float] = 0.34
    FONT_NAME_NORMAL: ClassVar[str] = "Helvetica"
    FONT_NAME_HEADER: ClassVar[str] = "Helvetica-Bold"
    FONT_NAME_SUBHEADER: ClassVar[str] = "Helvetica-Bold"
    FONT_NAME_SUBTITLE: ClassVar[str] = "Helvetica-Oblique"
    FONT_SIZE_NORMAL: ClassVar[int] = 10
    FONT_SIZE_HEADER: ClassVar[int] = 14
    FONT_SIZE_SUBHEADER: ClassVar[int] = 12
    FONT_SIZE_SUBTITLE: ClassVar[int] = 10
    ITEM_SPACING: ClassVar[float] = 0.1 * inch
    MARGIN_BOTTOM: ClassVar[float] = 0.25 * inch
    MARGIN_LEFT: ClassVar[float] = 0.25 * inch
    MARGIN_RIGHT: ClassVar[float] = 0.25 * inch
    MARGIN_TOP: ClassVar[float] = 0.25 * inch
    PAGE_SIZE: ClassVar[tuple[float, float]] = PageSize.LETTER.page_size
    SECTION_SPACING: ClassVar[float] = 0.3 * inch


class Colors(pydantic.BaseModel):
    primary: Color = pydantic.Field(default=Defaults.COLOR_PRIMARY, frozen=True)
    secondary: Color = pydantic.Field(default=Defaults.COLOR_SECONDARY, frozen=True)
    accent: Color = pydantic.Field(default=Defaults.COLOR_ACCENT, frozen=True)


class Margins(pydantic.BaseModel):
    left: float = pydantic.Field(default=Defaults.MARGIN_LEFT, frozen=True)
    right: float = pydantic.Field(default=Defaults.MARGIN_RIGHT, frozen=True)
    top: float = pydantic.Field(default=Defaults.MARGIN_TOP, frozen=True)
    bottom: float = pydantic.Field(default=Defaults.MARGIN_BOTTOM, frozen=True)


class Options(pydantic.BaseModel):
    item_spacing: float = pydantic.Field(default=Defaults.ITEM_SPACING, frozen=True)
    section_spacing: float = pydantic.Field(default=Defaults.SECTION_SPACING, frozen=True)
    column_gap: float = pydantic.Field(default=Defaults.COLUMN_GAP, frozen=True)
    column_split: float = pydantic.Field(default=Defaults.COLUMN_SPLIT, frozen=True)


class Page(pydantic.BaseModel):
    colors: Colors = pydantic.Field(default_factory=Colors, frozen=True)
    margins: Margins = pydantic.Field(default_factory=Margins, frozen=True)
    size: PageSize = pydantic.Field(default=PageSize.LETTER, frozen=True)
    options: Options = pydantic.Field(default_factory=Options, frozen=True)

    @pydantic.calculated_field
    @property
    def width(self) -> float:
        return self.size.page_size[0]

    @pydantic.calculated_field
    @property
    def height(self) -> float:
        return self.size.page_size[1]

    @pydantic.calculated_field
    @property
    def column_left_width(self) -> float:
        return self.width * self.options.column_split

    @pydantic.calculated_field
    @property
    def column_right_width(self) -> float:
        return self.width - self.column_left_width


class Config(pydantic.BaseModel):
    file: Path = pydantic.Field(frozen=True)
    page: Page = pydantic.Field(default_factory=Page, frozen=True)
    resume: Resume = pydantic.Field(frozen=True)
    styles: Styles = pydantic.Field(default_factory=Styles, frozen=True)
