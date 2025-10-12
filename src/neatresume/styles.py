# SPDX-FileCopyrightText: 2025-present Ricardo Rivera <silkrad@ririlabs.com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import enum
from uuid import uuid4

import pydantic
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import inch


class StyleFont(enum.StrEnum):
    HELVETICA = enum.auto()
    HELVETICA_BOLD = enum.auto()
    HELVETICA_OBLIQUE = enum.auto()
    SYMBOLA = enum.auto()

    @property
    def font_name(self) -> str:
        return self.value.title().replace("_", "-")


class Normal(pydantic.BaseModel, ParagraphStyle):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    alignment: int = pydantic.Field(default=TA_LEFT, frozen=True)
    fontName: str = pydantic.Field(default=StyleFont.HELVETICA.font_name, frozen=True)
    fontSize: float = pydantic.Field(default=10, frozen=True)
    leading: float = pydantic.Field(default=12, frozen=True)
    textColor: colors.Color = pydantic.Field(default_factory=lambda: colors.black, frozen=True)

    @property
    def style(self) -> ParagraphStyle:
        """Return a proper ReportLab ParagraphStyle object."""
        return ParagraphStyle(
            name=uuid4().hex,
            alignment=self.alignment,
            fontName=self.fontName,
            fontSize=self.fontSize,
            leading=self.leading,
            textColor=self.textColor,
        )


class Heading1(pydantic.BaseModel, ParagraphStyle):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    fontName: str = pydantic.Field(default=StyleFont.HELVETICA_BOLD.font_name, frozen=True)
    fontSize: float = pydantic.Field(default=18, frozen=True)
    leading: float = pydantic.Field(default=22, frozen=True)
    parent: ParagraphStyle = pydantic.Field(default_factory=Normal, frozen=True)
    spaceAfter: float = pydantic.Field(default=6, frozen=True)

    @property
    def style(self) -> ParagraphStyle:
        """Return a proper ReportLab ParagraphStyle object."""
        parent_style = self.parent.style if hasattr(self.parent, "style") else self.parent
        return ParagraphStyle(
            name=uuid4().hex,
            parent=parent_style,
            fontName=self.fontName,
            fontSize=self.fontSize,
            leading=self.leading,
            spaceAfter=self.spaceAfter,
        )


class Heading2(pydantic.BaseModel, ParagraphStyle):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    alignment: int = pydantic.Field(default=TA_CENTER, frozen=True)
    fontSize: float = pydantic.Field(default=14, frozen=True)
    leading: float = pydantic.Field(default=18, frozen=True)
    parent: ParagraphStyle = pydantic.Field(default_factory=Heading1, frozen=True)

    @property
    def style(self) -> ParagraphStyle:
        """Return a proper ReportLab ParagraphStyle object."""
        parent_style = self.parent.style if hasattr(self.parent, "style") else self.parent
        return ParagraphStyle(
            name=uuid4().hex,
            parent=parent_style,
            alignment=self.alignment,
            fontSize=self.fontSize,
            leading=self.leading,
        )


class CandidateName(pydantic.BaseModel, ParagraphStyle):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    alignment: int = pydantic.Field(default=TA_CENTER, frozen=True)
    parent: ParagraphStyle = pydantic.Field(default_factory=Heading1, frozen=True)
    spaceAfter: float = pydantic.Field(default=4, frozen=True)
    textColor: colors.Color = pydantic.Field(default_factory=lambda: colors.black, frozen=True)

    @property
    def style(self) -> ParagraphStyle:
        """Return a proper ReportLab ParagraphStyle object."""
        parent_style = self.parent.style if hasattr(self.parent, "style") else self.parent
        return ParagraphStyle(
            name=uuid4().hex,
            parent=parent_style,
            alignment=self.alignment,
            spaceAfter=self.spaceAfter,
            textColor=self.textColor,
        )


class CandidateTitle(pydantic.BaseModel, ParagraphStyle):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    alignment: int = pydantic.Field(default=TA_CENTER, frozen=True)
    fontSize: float = pydantic.Field(default=12, frozen=True)
    parent: ParagraphStyle = pydantic.Field(default_factory=Normal, frozen=True)
    spaceAfter: float = pydantic.Field(default=8, frozen=True)
    textColor: colors.Color = pydantic.Field(default_factory=lambda: colors.darkgray, frozen=True)

    @property
    def style(self) -> ParagraphStyle:
        """Return a proper ReportLab ParagraphStyle object."""
        parent_style = self.parent.style if hasattr(self.parent, "style") else self.parent
        return ParagraphStyle(
            name=uuid4().hex,
            parent=parent_style,
            alignment=self.alignment,
            fontSize=self.fontSize,
            spaceAfter=self.spaceAfter,
            textColor=self.textColor,
        )


class SectionHeader(pydantic.BaseModel, ParagraphStyle):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    fontSize: float = pydantic.Field(default=12, frozen=True)
    parent: ParagraphStyle = pydantic.Field(default_factory=Heading2, frozen=True)
    spaceBefore: float = pydantic.Field(default=12, frozen=True)
    spaceAfter: float = pydantic.Field(default=0, frozen=True)

    @property
    def style(self) -> ParagraphStyle:
        """Return a proper ReportLab ParagraphStyle object."""
        parent_style = self.parent.style if hasattr(self.parent, "style") else self.parent
        return ParagraphStyle(
            name=uuid4().hex,
            parent=parent_style,
            fontSize=self.fontSize,
            spaceBefore=self.spaceBefore,
            spaceAfter=self.spaceAfter,
        )


class BlockText(pydantic.BaseModel, ParagraphStyle):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    alignment: int = pydantic.Field(default=TA_JUSTIFY, frozen=True)
    fontSize: float = pydantic.Field(default=9, frozen=True)
    leftIndent: float = pydantic.Field(default=0.15 * inch, frozen=True)
    parent: ParagraphStyle = pydantic.Field(default_factory=Normal, frozen=True)
    spaceAfter: float = pydantic.Field(default=2, frozen=True)

    @property
    def style(self) -> ParagraphStyle:
        """Return a proper ReportLab ParagraphStyle object."""
        parent_style = self.parent.style if hasattr(self.parent, "style") else self.parent
        return ParagraphStyle(
            name=uuid4().hex,
            parent=parent_style,
            alignment=self.alignment,
            fontSize=self.fontSize,
            leftIndent=self.leftIndent,
            spaceAfter=self.spaceAfter,
        )


class BlockTitle(pydantic.BaseModel, ParagraphStyle):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    fontName: str = pydantic.Field(default=StyleFont.HELVETICA_BOLD.font_name, frozen=True)
    fontSize: float = pydantic.Field(default=10, frozen=True)
    leftIndent: float = pydantic.Field(default=0.15 * inch, frozen=True)
    parent: ParagraphStyle = pydantic.Field(default_factory=Normal, frozen=True)
    spaceBefore: float = pydantic.Field(default=4, frozen=True)
    spaceAfter: float = pydantic.Field(default=1, frozen=True)

    @property
    def style(self) -> ParagraphStyle:
        """Return a proper ReportLab ParagraphStyle object."""
        parent_style = self.parent.style if hasattr(self.parent, "style") else self.parent
        return ParagraphStyle(
            name=uuid4().hex,
            parent=parent_style,
            fontName=self.fontName,
            fontSize=self.fontSize,
            leftIndent=self.leftIndent,
            spaceBefore=self.spaceBefore,
            spaceAfter=self.spaceAfter,
        )


class BlockSubtitle(pydantic.BaseModel, ParagraphStyle):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    fontName: str = pydantic.Field(default=StyleFont.HELVETICA_OBLIQUE.font_name, frozen=True)
    fontSize: float = pydantic.Field(default=8, frozen=True)
    leftIndent: float = pydantic.Field(default=0.15 * inch, frozen=True)
    parent: ParagraphStyle = pydantic.Field(default_factory=Normal, frozen=True)
    spaceAfter: float = pydantic.Field(default=2, frozen=True)
    textColor: colors.Color = pydantic.Field(default_factory=lambda: colors.darkgray, frozen=True)

    @property
    def style(self) -> ParagraphStyle:
        """Return a proper ReportLab ParagraphStyle object."""
        parent_style = self.parent.style if hasattr(self.parent, "style") else self.parent
        return ParagraphStyle(
            name=uuid4().hex,
            parent=parent_style,
            fontName=self.fontName,
            fontSize=self.fontSize,
            leftIndent=self.leftIndent,
            spaceAfter=self.spaceAfter,
            textColor=self.textColor,
        )


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
