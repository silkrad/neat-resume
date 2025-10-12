# SPDX-FileCopyrightText: 2025-present Ricardo Rivera <silkrad@ririlabs.com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import enum

import pydantic
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import inch


class StyleName(enum.StrEnum):
    BLOCK_SUBTITLE = enum.auto()
    BLOCK_TEXT = enum.auto()
    BLOCK_TITLE = enum.auto()
    CANDIDATE_NAME = enum.auto()
    CANDIDATE_TITLE = enum.auto()
    HEADING1 = enum.auto()
    HEADING2 = enum.auto()
    LEFT_COLUMN_SUMMARY = enum.auto()
    LEFT_COLUMN_TEXT = enum.auto()
    NORMAL = enum.auto()
    SECTION_HEADER = enum.auto()

    @property
    def style_name(self) -> str:
        return self.value.title().replace("_", "")


class StyleFont(enum.StrEnum):
    HELVETICA = enum.auto()
    HELVETICA_BOLD = enum.auto()
    HELVETICA_OBLIQUE = enum.auto()
    SYMBOLA = enum.auto()

    @property
    def font_name(self) -> str:
        return self.value.title().replace("_", "-")


class Normal(pydantic.BaseModel, ParagraphStyle):
    name: str = pydantic.Field(default=StyleName.NORMAL.style_name, frozen=True)

    alignment: int = pydantic.Field(default=TA_LEFT, frozen=True)
    fontName: str = pydantic.Field(default=StyleFont.HELVETICA.font_name, frozen=True)
    fontSize: float = pydantic.Field(default=10, frozen=True)
    leading: float = pydantic.Field(default=12, frozen=True)
    textColor: colors.Color = pydantic.Field(default_factory=lambda: colors.black, frozen=True)


class Heading1(pydantic.BaseModel, ParagraphStyle):
    name: str = pydantic.Field(default=StyleName.HEADING1.style_name, frozen=True)

    fontName: str = pydantic.Field(default=StyleFont.HELVETICA_BOLD.font_name, frozen=True)
    fontSize: float = pydantic.Field(default=18, frozen=True)
    leading: float = pydantic.Field(default=22, frozen=True)
    parent: ParagraphStyle = pydantic.Field(default_factory=Normal, frozen=True)
    spaceAfter: float = pydantic.Field(default=6, frozen=True)


class Heading2(pydantic.BaseModel, ParagraphStyle):
    name: str = pydantic.Field(default=StyleName.HEADING2.style_name, frozen=True)

    alignment: int = pydantic.Field(default=TA_CENTER, frozen=True)
    fontSize: float = pydantic.Field(default=14, frozen=True)
    leading: float = pydantic.Field(default=18, frozen=True)
    parent: ParagraphStyle = pydantic.Field(default_factory=Heading1, frozen=True)


class CandidateName(pydantic.BaseModel, ParagraphStyle):
    name: str = pydantic.Field(default=StyleName.CANDIDATE_NAME.style_name, frozen=True)

    alignment: int = pydantic.Field(default=TA_CENTER, frozen=True)
    parent: ParagraphStyle = pydantic.Field(default_factory=Heading1, frozen=True)
    spaceAfter: float = pydantic.Field(default=4, frozen=True)
    textColor: colors.Color = pydantic.Field(default_factory=lambda: colors.black, frozen=True)


class CandidateTitle(pydantic.BaseModel, ParagraphStyle):
    name: str = pydantic.Field(default=StyleName.CANDIDATE_TITLE.style_name, frozen=True)

    alignment: int = pydantic.Field(default=TA_CENTER, frozen=True)
    fontSize: float = pydantic.Field(default=12, frozen=True)
    parent: ParagraphStyle = pydantic.Field(default_factory=Normal, frozen=True)
    spaceAfter: float = pydantic.Field(default=8, frozen=True)
    textColor: colors.Color = pydantic.Field(default_factory=lambda: colors.darkgray, frozen=True)


class SectionHeader(pydantic.BaseModel, ParagraphStyle):
    name: str = pydantic.Field(default=StyleName.SECTION_HEADER.style_name, frozen=True)

    fontSize: float = pydantic.Field(default=12, frozen=True)
    parent: ParagraphStyle = pydantic.Field(default_factory=Heading2, frozen=True)
    spaceBefore: float = pydantic.Field(default=12, frozen=True)
    spaceAfter: float = pydantic.Field(default=0, frozen=True)

class BlockText(pydantic.BaseModel, ParagraphStyle):
    name: str = pydantic.Field(default=StyleName.BLOCK_TEXT.style_name, frozen=True)

    alignment: int = pydantic.Field(default=TA_JUSTIFY, frozen=True)
    fontSize: float = pydantic.Field(default=9, frozen=True)
    leftIndent: float = pydantic.Field(default=0.15 * inch, frozen=True)
    parent: ParagraphStyle = pydantic.Field(default_factory=Normal, frozen=True)
    spaceAfter: float = pydantic.Field(default=2, frozen=True)

class BlockTitle(pydantic.BaseModel, ParagraphStyle):
    name: str = pydantic.Field(default=StyleName.BLOCK_TITLE.style_name, frozen=True)

    fontName: str = pydantic.Field(default=StyleFont.HELVETICA_BOLD.font_name, frozen=True)
    fontSize: float = pydantic.Field(default=10, frozen=True)
    leftIndent: float = pydantic.Field(default=0.15 * inch, frozen=True)
    parent: ParagraphStyle = pydantic.Field(default_factory=Normal, frozen=True)
    spaceBefore: float = pydantic.Field(default=4, frozen=True)
    spaceAfter: float = pydantic.Field(default=1, frozen=True)

class BlockSubtitle(pydantic.BaseModel, ParagraphStyle):
    name: str = pydantic.Field(default=StyleName.BLOCK_SUBTITLE.style_name, frozen=True)

    fontName: str = pydantic.Field(default=StyleFont.HELVETICA_OBLIQUE.font_name, frozen=True)
    fontSize: float = pydantic.Field(default=8, frozen=True)
    leftIndent: float = pydantic.Field(default=0.15 * inch, frozen=True)
    parent: ParagraphStyle = pydantic.Field(default_factory=Normal, frozen=True)
    spaceAfter: float = pydantic.Field(default=2, frozen=True)
    textColor: colors.Color = pydantic.Field(default_factory=lambda: colors.darkgray, frozen=True)


class Styles(pydantic.BaseModel):
    block_subtitle: BlockSubtitle = pydantic.Field(default_factory=BlockSubtitle, frozen=True)
    block_text: BlockText = pydantic.Field(default_factory=BlockText, frozen=True)
    block_title: BlockTitle = pydantic.Field(default_factory=BlockTitle, frozen=True)
    candidate_name: CandidateName = pydantic.Field(default_factory=CandidateName, frozen=True)
    candidate_title: CandidateTitle = pydantic.Field(default_factory=CandidateTitle, frozen=True)
    heading1: Heading1 = pydantic.Field(default_factory=Heading1, frozen=True)
    heading2: Heading2 = pydantic.Field(default_factory=Heading2, frozen=True)
    normal: Normal = pydantic.Field(default_factory=Normal, frozen=True)
    section_header: SectionHeader = pydantic.Field(default_factory=SectionHeader, frozen=True)
