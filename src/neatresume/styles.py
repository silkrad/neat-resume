# SPDX-FileCopyrightText: 2025-present Ricardo Rivera <silkrad@ririlabs.com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import enum
from uuid import uuid4

import pydantic
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from reportlab.lib.units import inch


class StyleFont(enum.StrEnum):
    HELVETICA = enum.auto()
    HELVETICA_BOLD = enum.auto()
    HELVETICA_OBLIQUE = enum.auto()
    SYMBOLA = enum.auto()

    @property
    def font_name(self) -> str:
        return self.value.title().replace("_", "-")


class Color(pydantic.BaseModel):
    hex_string: str = pydantic.Field(frozen=True)

    @property
    def hex_color(self) -> colors.Color:
        return colors.HexColor(self.hex_string)

    @pydantic.field_validator("hex_string", mode="before")
    @classmethod
    def validate_hex_color(cls, v) -> str:
        try:
            _ = colors.HexColor(v)
            return v
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid hex color '{v}': {e}") from e


class BaseStyleFactory(pydantic.BaseModel):
    alignment: int = pydantic.Field(default=TA_LEFT, ge=0, validate_default=True, frozen=True)
    fontName: str = pydantic.Field(default=StyleFont.HELVETICA.font_name, validate_default=True, frozen=True)
    fontSize: float = pydantic.Field(default=9, ge=0, validate_default=True, frozen=True)
    leading: float = pydantic.Field(default=11, ge=0, validate_default=True, frozen=True)
    leftIndent: float = pydantic.Field(default=0, ge=0, validate_default=True, frozen=True)
    rightIndent: float = pydantic.Field(default=0, ge=0, validate_default=True, frozen=True)
    spaceAfter: float = pydantic.Field(default=0, ge=0, validate_default=True, frozen=True)
    spaceBefore: float = pydantic.Field(default=0, ge=0, validate_default=True, frozen=True)
    textColor: Color = pydantic.Field(default_factory=lambda: Color(hex_string="#000000"), validate_default=True, frozen=True)

    def create_style(self, alignment: int | None = None, textColor: Color | None = None) -> ParagraphStyle:
        return ParagraphStyle(
            name=uuid4().hex,
            alignment=alignment if alignment else self.alignment,
            fontName=self.fontName,
            fontSize=self.fontSize,
            leading=self.leading,
            leftIndent=self.leftIndent,
            rightIndent=self.rightIndent,
            spaceAfter=self.spaceAfter,
            spaceBefore=self.spaceBefore,
            textColor=textColor.hex_color if textColor else self.textColor.hex_color,
        )


class CandidateNameStyleFactory(BaseStyleFactory):
    fontName: str = pydantic.Field(default=StyleFont.HELVETICA_BOLD.font_name, validate_default=True, frozen=True)
    fontSize: float = pydantic.Field(default=18, ge=0, validate_default=True, frozen=True)
    leading: float = pydantic.Field(default=22, ge=0, validate_default=True, frozen=True)
    spaceAfter: float = pydantic.Field(default=4, validate_default=True, frozen=True)


class CandidateTitleStyleFactory(BaseStyleFactory):
    fontSize: float = pydantic.Field(default=12, validate_default=True, frozen=True)
    spaceAfter: float = pydantic.Field(default=8, validate_default=True, frozen=True)
    textColor: Color = pydantic.Field(default_factory=lambda: Color(hex_string="#A9A9A9"), validate_default=True, frozen=True)


class SectionHeaderStyleFactory(BaseStyleFactory):
    fontName: str = pydantic.Field(default=StyleFont.HELVETICA_BOLD.font_name, validate_default=True, frozen=True)
    fontSize: float = pydantic.Field(default=12, validate_default=True, frozen=True)
    leading: float = pydantic.Field(default=18, validate_default=True, frozen=True)
    spaceBefore: float = pydantic.Field(default=12, validate_default=True, frozen=True)
    spaceAfter: float = pydantic.Field(default=0, validate_default=True, frozen=True)


class SectionSubtitleStyleFactory(BaseStyleFactory):
    fontName: str = pydantic.Field(default=StyleFont.HELVETICA_OBLIQUE.font_name, validate_default=True, frozen=True)
    fontSize: float = pydantic.Field(default=10, validate_default=True, frozen=True)
    leftIndent: float = pydantic.Field(default=0.1 * inch, validate_default=True, frozen=True)
    spaceAfter: float = pydantic.Field(default=2, validate_default=True, frozen=True)
    textColor: Color = pydantic.Field(default_factory=lambda: Color(hex_string="#696969"), validate_default=True, frozen=True)


class SectionTextStyleFactory(BaseStyleFactory):
    alignment: int = pydantic.Field(default=TA_JUSTIFY, validate_default=True, frozen=True)
    fontSize: float = pydantic.Field(default=9, validate_default=True, frozen=True)
    leftIndent: float = pydantic.Field(default=0.1 * inch, validate_default=True, frozen=True)
    spaceAfter: float = pydantic.Field(default=2, validate_default=True, frozen=True)


class SectionTitleStyleFactory(BaseStyleFactory):
    fontName: str = pydantic.Field(default=StyleFont.HELVETICA_BOLD.font_name, validate_default=True, frozen=True)
    fontSize: float = pydantic.Field(default=11, validate_default=True, frozen=True)
    spaceBefore: float = pydantic.Field(default=4, validate_default=True, frozen=True)
    spaceAfter: float = pydantic.Field(default=1, validate_default=True, frozen=True)


class SideBarSubtitleStyleFactory(BaseStyleFactory):
    fontName: str = pydantic.Field(default=StyleFont.HELVETICA_BOLD.font_name, validate_default=True, frozen=True)
    fontSize: float = pydantic.Field(default=9, validate_default=True, frozen=True)
    leftIndent: float = pydantic.Field(default=0.1 * inch, validate_default=True, frozen=True)
    spaceAfter: float = pydantic.Field(default=2, validate_default=True, frozen=True)
    textColor: Color = pydantic.Field(default_factory=lambda: Color(hex_string="#696969"), validate_default=True, frozen=True)


class SideBarSummaryStyleFactory(BaseStyleFactory):
    fontSize: float = pydantic.Field(default=9, validate_default=True, frozen=True)
    spaceAfter: float = pydantic.Field(default=2, validate_default=True, frozen=True)


class SideBarTextStyleFactory(BaseStyleFactory):
    fontSize: float = pydantic.Field(default=9, validate_default=True, frozen=True)
    leftIndent: float = pydantic.Field(default=0 * inch, validate_default=True, frozen=True)
    spaceAfter: float = pydantic.Field(default=2, validate_default=True, frozen=True)


class SideBarTitleStyleFactory(BaseStyleFactory):
    fontName: str = pydantic.Field(default=StyleFont.HELVETICA_BOLD.font_name, validate_default=True, frozen=True)
    fontSize: float = pydantic.Field(default=9, validate_default=True, frozen=True)
    spaceBefore: float = pydantic.Field(default=8, validate_default=True, frozen=True)
    spaceAfter: float = pydantic.Field(default=0, validate_default=True, frozen=True)


class Styles(pydantic.BaseModel):
    candidate_name: CandidateNameStyleFactory = pydantic.Field(default_factory=CandidateNameStyleFactory, frozen=True)
    candidate_title: CandidateTitleStyleFactory = pydantic.Field(default_factory=CandidateTitleStyleFactory, frozen=True)
    normal: BaseStyleFactory = pydantic.Field(default_factory=BaseStyleFactory, frozen=True)
    section_header: SectionHeaderStyleFactory = pydantic.Field(default_factory=SectionHeaderStyleFactory, frozen=True)
    section_subtitle: SectionSubtitleStyleFactory = pydantic.Field(default_factory=SectionSubtitleStyleFactory, frozen=True)
    section_text: SectionTextStyleFactory = pydantic.Field(default_factory=SectionTextStyleFactory, frozen=True)
    section_title: SectionTitleStyleFactory = pydantic.Field(default_factory=SectionTitleStyleFactory, frozen=True)
    sidebar_subtitle: SideBarSubtitleStyleFactory = pydantic.Field(default_factory=SideBarSubtitleStyleFactory, frozen=True)
    sidebar_summary: SideBarSummaryStyleFactory = pydantic.Field(default_factory=SideBarSummaryStyleFactory, frozen=True)
    sidebar_text: SideBarTextStyleFactory = pydantic.Field(default_factory=SideBarTextStyleFactory, frozen=True)
    sidebar_title: SideBarTitleStyleFactory = pydantic.Field(default_factory=SideBarTitleStyleFactory, frozen=True)
