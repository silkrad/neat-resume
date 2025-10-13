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
from typing import Any, ClassVar

import pydantic
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.lib import colors
from reportlab.platypus.frames import Frame
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Line, Drawing

from neatresume.config import Config, Page
from neatresume.resume import CandidateInfo, EducationBlock, CertificationBlock
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
            width=self.page.column_left_width - self.page.options.column_gap,  # Small gap between columns
            height=self.page.height,
            id=TemplateID.FRAME_LEFT,
            showBoundary=0,
        )
        right_frame = Frame(
            x1=self.page.margins.left + self.page.column_left_width + self.page.options.column_gap,
            y1=self.page.margins.bottom,
            width=self.page.column_right_width - self.page.options.column_gap,
            height=self.page.height,
            id=TemplateID.FRAME_RIGHT,
            showBoundary=0,
        )
        frames.append(left_frame)
        frames.append(right_frame)
        return PageTemplate(id=TemplateID.TEMPLATE_MULTI_COLUMN, onPage=self._on_page_multi_column, frames=frames)

    def _on_page_multi_column(self, canvas: Canvas, doc: BaseDocTemplate) -> None:
        _ = doc
        # Match old generator: tint entire left column area including gap
        column_boundary = self.page.margins.left + self.page.column_left_width
        canvas.saveState()
        canvas.setFillColor(self.page.colors.accent.hex_color)
        canvas.rect(0, 0, column_boundary, self.page.height_full, fill=1, stroke=0)
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
        doc = self._document
        doc.addPageTemplates([self._template_multi_column])
        story: list = []
        story.extend(self._build_candidate_header(self.config.resume.candidate))
        story.append(Spacer(1, 0.1 * inch))
        story.extend(self._build_professional_summary_left(self.config.resume.summary))
        story.extend(self._build_contact_info(self.config.resume.candidate))
        story.extend(self._build_skills_section(self.config.resume.skills))
        story.extend(self._build_education_section(self.config.resume.education))
        if self.config.resume.certifications:
            story.extend(self._build_certifications_section(self.config.resume.certifications))
        story.extend(self._frame_break())
        story.extend(self._build_experience_section(self.config.resume.experience))
        if self.config.resume.sections:
            story.extend(self._build_custom_sections(self.config.resume.sections))
        doc.build(story)

    def _create_section_header(self, title: str) -> list[Any]:
        elements = []
        elements.append(Paragraph(title, self.config.styles.section_header.create_style()))
        line_width = (self.config.page.column_left_width - self.config.page.options.column_gap) - 0.15 * inch
        line_drawing = Drawing(line_width, 3)
        line = Line(0, 1, line_width, 1)
        line.strokeColor = colors.black
        line.strokeWidth = 1
        line_drawing.add(line)
        elements.append(line_drawing)
        elements.append(Spacer(1, 0.02 * inch))
        return elements

    def _frame_break(self) -> list[Any]:
        """Create a frame break to move to the next column."""
        from reportlab.platypus.doctemplate import FrameBreak

        return [FrameBreak()]

    def _build_candidate_header(self, candidate: CandidateInfo) -> list[Any]:
        elements = []
        elements.append(Paragraph(candidate.name, self.config.styles.candidate_name.create_style()))
        elements.append(Paragraph(candidate.title, self.config.styles.candidate_title.create_style()))
        return elements

    def _build_contact_info(self, candidate: CandidateInfo) -> list[Any]:
        elements = []
        elements.extend(self._create_section_header("CONTACT"))

        def format_contact_line(icon: str, text: str) -> str:
            try:
                pdfmetrics.getFont("Symbola")
                return f'<font name="Symbola">{icon}</font> {text}'
            except Exception:
                return f"{icon} {text}"

        contact_info = [
            format_contact_line("\U0001f4de", candidate.phone_regional),
            format_contact_line("\U0001f582", candidate.email),
        ]
        if candidate.address:
            contact_info.append(format_contact_line("\U0001f4cd", candidate.address))
        if candidate.website:
            contact_info.append(format_contact_line("\U0001f310", candidate.website))
        if candidate.linkedin:
            contact_info.append(format_contact_line("\U0001f310", "LinkedIn"))
        if candidate.github:
            contact_info.append(format_contact_line("\U0001f310", "GitHub"))
        if candidate.gitlab:
            contact_info.append(format_contact_line("\U0001f310", "GitLab"))
        for info in contact_info:
            elements.append(Paragraph(info, self.config.styles.normal.create_style()))
        elements.append(Spacer(1, 0.05 * inch))
        return elements

    def _build_professional_summary_left(self, summary: str) -> list[Any]:
        elements = []
        elements.append(Paragraph(summary, self.config.styles.normal.create_style()))
        elements.append(Spacer(1, 0.05 * inch))
        return elements

    def _build_skills_section(self, skills: dict[str, list[str]]) -> list[Any]:
        elements = []
        elements.extend(self._create_section_header("SKILLS"))
        skill_categories = list(skills.items())
        for i, (category, skill_list) in enumerate(skill_categories):
            elements.append(Paragraph(f"<b>{category.upper()}</b>", self.config.styles.section_text.create_style()))
            skills_text = " • ".join(skill_list)
            elements.append(Paragraph(skills_text, self.config.styles.section_text.create_style()))
            if i < len(skill_categories) - 1:
                elements.append(Spacer(1, 0.08 * inch))
            else:
                elements.append(Spacer(1, 0.02 * inch))
        elements.append(Spacer(1, 0.05 * inch))
        return elements

    def _build_education_section(self, education: list[EducationBlock]) -> list[Any]:
        elements = []
        elements.extend(self._create_section_header("EDUCATION"))

        for edu in education:
            elements.append(Paragraph(f"<b>{edu.degree}</b>", self.config.styles.section_text.create_style()))
            elements.append(Paragraph(f"{edu.field_of_study}", self.config.styles.section_text.create_style()))
            elements.append(Paragraph(f"{edu.institution}", self.config.styles.section_text.create_style()))
            if edu.location:
                elements.append(Paragraph(f"{edu.location}", self.config.styles.section_text.create_style()))
            end_date = edu.end_date.strftime("%Y") if edu.end_date else "Present"
            start_date = edu.start_date.strftime("%Y")
            elements.append(Paragraph(f"{start_date} - {end_date}", self.config.styles.section_text.create_style()))
            if edu.gpa:
                elements.append(Paragraph(f"GPA: {edu.gpa:.2f}", self.config.styles.section_text.create_style()))
            elements.append(Spacer(1, 0.05 * inch))
        return elements

    def _build_certifications_section(self, certifications: list[CertificationBlock]) -> list[Any]:
        elements = []
        elements.extend(self._create_section_header("CERTIFICATIONS"))

        for cert in certifications:
            elements.append(Paragraph(f"<b>{cert.title}</b>", self.config.styles.section_text.create_style()))
            if cert.issue_date:
                issue_date = cert.issue_date.strftime("%Y")
                elements.append(Paragraph(f"{issue_date}", self.config.styles.section_text.create_style()))
            elements.append(Spacer(1, 0.02 * inch))
        return elements

    def _build_experience_section(self, experience: list) -> list[Any]:
        elements = []
        elements.extend(self._create_section_header("WORK EXPERIENCE"))
        for exp in experience:
            elements.append(Paragraph(f"{exp.position}", self.config.styles.section_text.create_style()))
            end_date = exp.end_date.strftime("%b %Y") if exp.end_date else "Present"
            start_date = exp.start_date.strftime("%b %Y")
            company_info = f"{exp.company} | {start_date} - {end_date}"
            elements.append(Paragraph(company_info, self.config.styles.section_text.create_style()))
            if exp.summary:
                for point in exp.summary:
                    elements.append(Paragraph(f"• {point}", self.config.styles.section_text.create_style()))
            elements.append(Spacer(1, 0.05 * inch))
        return elements

    def _build_custom_sections(self, custom_sections: dict[str, list]) -> list[Any]:
        elements = []
        for section_title, blocks in custom_sections.items():
            elements.extend(self._create_section_header(section_title.upper()))
            for block in blocks:
                if hasattr(block, "title"):
                    elements.append(Paragraph(f"<b>{block.title}</b>", self.config.styles.section_title.create_style()))
                if hasattr(block, "subtitle") and block.subtitle:
                    elements.append(Paragraph(block.subtitle, self.config.styles.section_subtitle.create_style()))
                if hasattr(block, "summary") and block.summary:
                    for point in block.summary:
                        elements.append(Paragraph(f"• {point}", self.config.styles.section_text.create_style()))
                elements.append(Spacer(1, 0.05 * inch))
        return elements
