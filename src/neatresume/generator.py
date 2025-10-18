# SPDX-FileCopyrightText: 2025-present Ricardo Rivera <silkrad@ririlabs.com>
#
# SPDX-License-Identifier: Apache-2.0

"""PDF resume generator using ReportLab.

This module provides functionality to generate professional PDF resumes
from ResumeData models using ReportLab with a two-column layout.
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import ClassVar

import pydantic
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, FrameBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.platypus.frames import Frame
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, HRFlowable, Table, Flowable
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from neatresume.config import Config, Page
from neatresume.styles import StyleFont, Symbol


class TemplateID:
    FRAME_MAIN: ClassVar[str] = uuid.uuid4().hex
    FRAME_SIDEBAR: ClassVar[str] = uuid.uuid4().hex
    TEMPLATE_MULTI_COLUMN: ClassVar[str] = uuid.uuid4().hex


class BaseDocumentFactory(pydantic.BaseModel):
    file: Path = pydantic.Field(frozen=True)
    page: Page = pydantic.Field(frozen=True)

    def create_document(self) -> BaseDocTemplate:
        return BaseDocTemplate(
            filename=self.file.as_posix(),
            pagesize=self.page.paper.size,
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
            width=self.page.sidebar_width - self.page.options.column_gap,
            height=self.page.content_height,
            id=TemplateID.FRAME_SIDEBAR,
            showBoundary=0,
        )
        right_frame = Frame(
            x1=self.page.margins.left + self.page.sidebar_width + self.page.options.column_gap,
            y1=self.page.margins.bottom,
            width=self.page.main_width - self.page.options.column_gap,
            height=self.page.content_height,
            id=TemplateID.FRAME_MAIN,
            showBoundary=0,
        )
        frames.append(left_frame)
        frames.append(right_frame)
        return PageTemplate(id=TemplateID.TEMPLATE_MULTI_COLUMN, onPage=self._on_page_multi_column, frames=frames)

    def _on_page_multi_column(self, canvas: Canvas, doc: BaseDocTemplate) -> None:
        _ = doc
        column_boundary = self.page.margins.left + self.page.sidebar_width
        canvas.saveState()
        canvas.setFillColor(self.page.colors.frame_left.hex_color)
        canvas.rect(0, 0, column_boundary, self.page.page_height, fill=1, stroke=0)
        canvas.setFillColor(self.page.colors.frame_right.hex_color)
        canvas.rect(column_boundary, 0, self.page.main_width, self.page.page_height, fill=1, stroke=0)
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

    def generate(self) -> None:
        document = self._document
        document.addPageTemplates([self._template_multi_column])
        flowables: list[Flowable] = []
        flowables.extend(self._generate_frame_left())
        flowables.extend([FrameBreak()])
        flowables.extend(self._generate_frame_main())
        document.build(flowables)

    def _generate_frame_left(self) -> list[Flowable]:
        elements: list[Flowable] = []
        elements.extend(self._build_candidate_header())
        elements.extend(self._build_professional_summary())
        elements.extend(self._build_contact_info())
        if len(self.config.resume.education) > 0:
            elements.extend(self._build_education_section())
        if len(self.config.resume.recognitions) > 0:
            elements.extend(self._build_recognitions_section())
        if len(self.config.resume.skills) > 0:
            elements.extend(self._build_skills_section())
        return elements

    def _generate_frame_main(self) -> list[Flowable]:
        elements: list[Flowable] = []
        if len(self.config.resume.experience) > 0:
            elements.extend(self._build_experience_section())
        if len(self.config.resume.sections) > 0:
            elements.extend(self._build_custom_sections())
        return elements

    def _add_header(self, title: str, style: ParagraphStyle) -> list[Flowable]:
        elements: list[Flowable] = []
        elements.append(Paragraph(title, style))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.black))
        return elements

    def _build_candidate_header(self) -> list[Flowable]:
        elements: list[Flowable] = []
        elements.append(Paragraph(self.config.resume.candidate.name, self.config.styles.candidate_name.get_style()))
        elements.append(Paragraph(self.config.resume.candidate.title, self.config.styles.candidate_title.get_style()))
        return elements

    def _build_contact_info(self) -> list[Flowable]:
        elements: list[Flowable] = []
        elements.extend(self._add_header(self.config.resume.section_names.contact, self.config.styles.sidebar_title.get_style()))
        contact_info: list[str] = []
        contact_info.append(self._format_contact_line(Symbol.PHONE, self.config.resume.candidate.phone_regional))
        contact_info.append(
            self._format_contact_line(
                Symbol.EMAIL, f'<link href="mailto:{self.config.resume.candidate.email}">{self.config.resume.candidate.email}</link>'
            )
        )
        if self.config.resume.candidate.address:
            contact_info.append(self._format_contact_line(Symbol.ADDRESS, self.config.resume.candidate.address))
        if self.config.resume.candidate.website:
            contact_info.append(
                self._format_contact_line(Symbol.WEBSITE, f'<link href="{self.config.resume.candidate.website}">Website</link>')
            )
        if self.config.resume.candidate.linkedin:
            contact_info.append(
                self._format_contact_line(Symbol.LINKEDIN, f'<link href="{self.config.resume.candidate.linkedin}">LinkedIn</link>')
            )
        if self.config.resume.candidate.github:
            contact_info.append(
                self._format_contact_line(Symbol.GITHUB, f'<link href="{self.config.resume.candidate.github}">GitHub</link>')
            )
        if self.config.resume.candidate.gitlab:
            contact_info.append(
                self._format_contact_line(Symbol.GITLAB, f'<link href="{self.config.resume.candidate.gitlab}">GitLab</link>')
            )
        for info in contact_info:
            elements.append(Paragraph(info, self.config.styles.sidebar_text.get_style()))
        return elements

    def _build_professional_summary(self) -> list[Flowable]:
        elements: list[Flowable] = []
        elements.append(Paragraph(self.config.resume.summary, self.config.styles.sidebar_summary.get_style()))
        return elements

    def _build_skills_section(self) -> list[Flowable]:
        elements: list[Flowable] = []
        elements.extend(self._add_header(self.config.resume.section_names.skills, self.config.styles.sidebar_title.get_style()))
        for category, skill_list in self.config.resume.skills.items():
            elements.append(Paragraph(f"{category.upper()}", self.config.styles.sidebar_subtitle.get_style()))
            skills_text = " • ".join(skill_list)
            elements.append(Paragraph(skills_text, self.config.styles.sidebar_text.get_style()))
        return elements

    def _build_education_section(self) -> list[Flowable]:
        elements: list[Flowable] = []
        elements.extend(self._add_header(self.config.resume.section_names.education, self.config.styles.sidebar_title.get_style()))
        for edu in self.config.resume.education:
            elements.append(Paragraph(f"{edu.degree}", self.config.styles.sidebar_subtitle.get_style()))
            elements.append(Paragraph(f"{edu.institution}", self.config.styles.sidebar_text.get_style()))
            if edu.location:
                elements.append(Paragraph(f"{edu.location}", self.config.styles.sidebar_text.get_style()))
            start_date = edu.start_date.strftime("%b %Y")
            end_date = edu.end_date.strftime("%b %Y") if edu.end_date else "Present"
            elements.append(Paragraph(f"{start_date} - {end_date}", self.config.styles.sidebar_text.get_style()))
            if edu.gpa:
                elements.append(Paragraph(f"GPA: {edu.gpa:.2f}", self.config.styles.sidebar_text.get_style()))
            elements.append(Spacer(1, 0.05 * inch))
        return elements

    def _build_recognitions_section(self) -> list[Flowable]:
        elements: list[Flowable] = []
        elements.extend(self._add_header(self.config.resume.section_names.recognitions, self.config.styles.sidebar_title.get_style()))
        data = []
        for recognition in self.config.resume.recognitions:
            left_style = self.config.styles.sidebar_text.get_style(alignment=TA_LEFT)
            right_style = self.config.styles.sidebar_text.get_style(alignment=TA_RIGHT)
            recognition_data = [
                Paragraph(" • " + recognition.name, left_style),
                Paragraph(recognition.issue_date.strftime("%Y") if recognition.issue_date else "", right_style),
            ]
            data.append(recognition_data)
        table = Table(data, colWidths=[None, self.config.styles.recognition_table.date_width])
        table.setStyle(self.config.styles.recognition_table.get_style())
        elements.append(table)
        return elements

    def _build_experience_section(self) -> list[Flowable]:
        elements: list[Flowable] = []
        elements.extend(self._add_header("Professional Experience", self.config.styles.section_title.get_style()))
        table_style = self.config.styles.experience_table.get_style()
        for exp in self.config.resume.experience:
            company_and_location_data = [
                [
                    Paragraph(f"{exp.company}", self.config.styles.section_title.get_style(alignment=TA_LEFT)),
                    Paragraph(f"{exp.location}", self.config.styles.section_subsubtitle.get_style(alignment=TA_RIGHT))
                    if exp.location
                    else Paragraph(""),
                ]
            ]
            company_and_location = Table(company_and_location_data, colWidths=[None, self.config.styles.experience_table.location_width])
            company_and_location.setStyle(table_style)
            elements.append(company_and_location)
            title_and_dates_data = [
                [
                    Paragraph(exp.position, self.config.styles.section_subtitle.get_style(alignment=TA_LEFT)),
                    Paragraph(
                        f"{exp.start_date.strftime('%b %Y')} - {exp.end_date.strftime('%b %Y') if exp.end_date else 'Present'}",
                        self.config.styles.section_subsubtitle.get_style(alignment=TA_RIGHT),
                    ),
                ]
            ]
            title_and_dates = Table(title_and_dates_data, colWidths=[None, self.config.styles.experience_table.date_width])
            title_and_dates.setStyle(table_style)
            elements.append(title_and_dates)
            for point in exp.summary:
                elements.append(Paragraph(f"• {point}", self.config.styles.section_text.get_style()))
        return elements

    def _build_custom_sections(self) -> list[Flowable]:
        elements: list[Flowable] = []
        for section_title, blocks in self.config.resume.sections.items():
            elements.extend(self._add_header(section_title, self.config.styles.section_title.get_style()))
            for block in blocks:
                if hasattr(block, "title"):
                    elements.append(Paragraph(f"<b>{block.title}</b>", self.config.styles.section_title.get_style()))
                if hasattr(block, "subtitle") and block.subtitle:
                    elements.append(Paragraph(block.subtitle, self.config.styles.section_subtitle.get_style()))
                if hasattr(block, "summary") and block.summary:
                    for point in block.summary:
                        elements.append(Paragraph(f"• {point}", self.config.styles.section_text.get_style()))
                elements.append(Spacer(1, 0.05 * inch))
        return elements

    def _format_contact_line(self, icon: Symbol, text: str) -> str:
        try:
            pdfmetrics.getFont(StyleFont.SYMBOLA.font_name)
            return f'<font name="{StyleFont.SYMBOLA.font_name}">{icon.value}</font> {text}'
        except Exception:
            return f"{icon.value} {text}"
