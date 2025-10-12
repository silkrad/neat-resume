# SPDX-FileCopyrightText: 2025-present Ricardo Rivera <silkrad@ririlabs.com>
#
# SPDX-License-Identifier: Apache-2.0

"""PDF resume generator using ReportLab.

This module provides functionality to generate professional PDF resumes
from ResumeData models using ReportLab with a two-column layout.
"""

from __future__ import annotations

import enum
import uuid
from pathlib import Path
from typing import Any, ClassVar

import pydantic
from reportlab.lib import styles
from reportlab.lib.styles import ParagraphStyle, StyleSheet1
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus.frames import Frame
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

from neatresume.config import Config, Page
from neatresume.styles import StyleFont


class TemplateID:
    FRAME_FOOTER: ClassVar[str] = uuid.uuid4().hex
    FRAME_LEFT: ClassVar[str] = uuid.uuid4().hex
    FRAME_RIGHT: ClassVar[str] = uuid.uuid4().hex
    FRAME_SIDE: ClassVar[str] = uuid.uuid4().hex
    TEMPLATE_MULTI_COLUMN: ClassVar[str] = uuid.uuid4().hex


class BaseDocumentFactory(pydantic.BaseModel):
    file: Path = pydantic.Field(frozen=True)
    page: Page = pydantic.Field(frozen=True)

    def create_document(self) -> BaseDocTemplate:
        return BaseDocTemplate(
            filename=self.file.as_posix(),
            pagesize=self.page.size.page_size,
            leftMargin=self.page.margins.left,
            rightMargin=self.page.margins.right,
            topMargin=self.page.margins.top,
            bottomMargin=self.page.margins.bottom,
        )


class PageTemplateFactory(pydantic.BaseModel):
    page: Page = pydantic.Field(frozen=True)

    def create_template_multi_column(self) -> PageTemplate:
        frames: list[Frame] = []
        left_frame = Frame(
            x1=self.page.margins.left,
            y1=self.page.margins.bottom,
            width=self.page.column_left_width,
            height=self.page.height,
            id=TemplateID.FRAME_LEFT,
            showBoundary=0,
        )
        right_frame = Frame(
            x1=self.page.margins.left + self.page.column_left_width,
            y1=self.page.margins.bottom,
            width=self.page.column_right_width,
            height=self.page.height,
            id=TemplateID.FRAME_RIGHT,
            showBoundary=0,
        )
        frames.append(left_frame)
        frames.append(right_frame)
        return PageTemplate(id=TemplateID.TEMPLATE_MULTI_COLUMN, beforeDrawPage=self._before_draw_page_multi_column, frames=frames)

    def _before_draw_page_multi_column(self, canvas: Canvas, doc: BaseDocTemplate) -> None:
        _ = doc
        column_boundary = self.page.margins.left + self.page.column_left_width
        canvas.saveState()
        canvas.setFillColor(self.page.colors.accent)
        canvas.rect(0, 0, column_boundary, self.page.height, fill=1, stroke=0)
        canvas.restoreState()


class Generator(pydantic.BaseModel):
    config: Config = pydantic.Field(frozen=True)

    _document: BaseDocTemplate = pydantic.PrivateAttr()
    _template_multi_column: PageTemplate = pydantic.PrivateAttr()

    def model_post_init(self, _: object) -> None:
        document_factory = BaseDocumentFactory(file=self.config.file, page=self.config.page)
        template_factory = PageTemplateFactory(page=self.config.page)
        self._document = document_factory.create_document()
        self._template_multi_column = template_factory.create_template_multi_column()
        pdfmetrics.registerFont(TTFont(StyleFont.SYMBOLA.font_name, "/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf"))

    def generate(self, **kwargs: Any) -> None:
        doc = self._document
        doc.addPageTemplates([self._template_multi_column])
        story: list = []

        doc.build(story)  # Placeholder for the story list
