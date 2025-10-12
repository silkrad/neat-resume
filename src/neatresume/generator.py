# SPDX-FileCopyrightText: 2025-present Ricardo Rivera <silkrad@ririlabs.com>
#
# SPDX-License-Identifier: Apache-2.0

"""PDF resume generator using ReportLab.

This module provides functionality to generate professional PDF resumes
from ResumeData models using ReportLab with a two-column layout.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black, darkgray, lightgrey, HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.graphics.shapes import Line, Drawing
from reportlab.graphics import renderPDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .resume_data import ResumeData, CandidateInfo, EducationBlock, CertificationBlock


class LeftColumnOverflowError(Exception):
    """Raised when the left column content spills into the right column."""
    
    def __init__(self, page_number: int) -> None:
        """Initialize with page details.
        
        Args:
            page_number: The page number where the overflow was detected.
        """
        self.page_number = page_number
        super().__init__(
            f"Left column content spilled into the right column on page {page_number}. "
            f"Please reduce content in the left column sections (professional summary, "
            f"contact info, skills, education, or certifications) to fit within one page."
        )


class ColumnAwareDoc(BaseDocTemplate):
    """Detect true column overflow and page changes using handle_flowable."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_page = 1
        self._last_frame = 0
        self._left_column_finished = False
        self._in_left_column_content = False

    def handle_flowable(self, flowables):
        """Called each time a flowable is drawn or moved."""
        # Before drawing, record the page/frame
        current_page = self.page
        try:
            frame_index = self.pageTemplate.frames.index(self.frame)
        except (AttributeError, ValueError):
            frame_index = 0

        # Call normal behavior
        super().handle_flowable(flowables)

        new_page = self.page
        try:
            new_frame_index = self.pageTemplate.frames.index(self.frame)
        except (AttributeError, ValueError):
            new_frame_index = 0

        # Track if we're processing left column content
        if new_frame_index == 0:  # Left column
            self._in_left_column_content = True
        elif new_frame_index == 1 and self._in_left_column_content and not self._left_column_finished:
            # We've spilled to right column but haven't marked left column as finished
            # This indicates overflow
            raise LeftColumnOverflowError(new_page)

        self._last_page = new_page
        self._last_frame = new_frame_index

    def mark_left_column_finished(self):
        """Mark that left column content is intentionally finished."""
        self._left_column_finished = True


class TintedPageTemplate(PageTemplate):
    """Custom PageTemplate with a tinted background for the left column."""
    
    def __init__(self, left_col_width: float, page_width: float, page_height: float, 
                 left_margin: float, **kwargs: Any) -> None:
        """Initialize with page dimensions for background drawing."""
        super().__init__(**kwargs)
        self.left_col_width = left_col_width
        self.page_width = page_width
        self.page_height = page_height
        self.left_margin = left_margin
        # Professional cool tint - darker blue-gray
        self.tint_color = HexColor('#e1e8f0')  # Darker bluish gray
    
    def beforeDrawPage(self, canvas: Any, doc: Any) -> None:
        """Draw the tinted background before page content."""
        canvas.saveState()
        
        # Set fill color for left column background
        canvas.setFillColor(self.tint_color)
        
        # Draw background rectangle for left column extending to all edges
        # Start from left page edge (0) and go to column boundary
        column_boundary = self.left_margin + self.left_col_width + 0.05*inch  # Small overlap into gap
        canvas.rect(
            0,  # Start from left page edge
            0,  # Start from bottom page edge
            column_boundary,  # Width extends to column boundary
            self.page_height,  # Full page height
            fill=1,
            stroke=0
        )
        
        canvas.restoreState()


class ResumeGenerator:
    """Generate professional PDF resumes from ResumeData models.
    
    This generator creates a two-column layout with candidate info, skills,
    education, and certifications on the left (34%) and work experience
    and custom sections on the right (66%).
    """
    
    def __init__(self) -> None:
        """Initialize the resume generator with default styling."""
        self.styles = getSampleStyleSheet()
        self._register_fonts()
        self._setup_custom_styles()
        # Column widths will be set during PDF generation
        self.left_col_width: float = 0
        self.right_col_width: float = 0
        
    def _register_fonts(self) -> None:
        """Register additional fonts including Symbola for Unicode support."""
        try:
            # Try to register Symbola font for Unicode symbols using system path
            pdfmetrics.registerFont(TTFont('Symbola', '/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf'))
        except Exception as e:
            print(f"Warning: Could not register Symbola font: {e}")
            # If Symbola font is not available, continue without it
            # The Unicode characters will still work with default fonts in most cases
            pass
        
    def _setup_custom_styles(self) -> None:
        """Set up custom paragraph styles for the resume."""
        # Header styles
        self.styles.add(ParagraphStyle(
            name='CandidateName',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=4,
            textColor=black,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CandidateTitle',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=8,
            textColor=darkgray,
            alignment=TA_CENTER
        ))
        
        # Section headers
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceBefore=12,
            spaceAfter=0,
            textColor=black,
            fontName='Helvetica-Bold'
        ))
        
        # Left column styles (smaller font for one-page fit)
        self.styles.add(ParagraphStyle(
            name='LeftColumnText',
            parent=self.styles['Normal'],
            fontSize=8,
            spaceAfter=2,
            alignment=TA_LEFT,
            leftIndent=0.15*inch  # Indent content under headers
        ))
        
        self.styles.add(ParagraphStyle(
            name='LeftColumnHeader',
            parent=self.styles['SectionHeader'],
            fontSize=9,
            spaceBefore=8,
            spaceAfter=0
        ))
        
        self.styles.add(ParagraphStyle(
            name='LeftColumnSummary',
            parent=self.styles['Normal'],
            fontSize=8,
            spaceAfter=2,
            alignment=TA_JUSTIFY,
            leftIndent=0  # No indentation for summary
        ))
        
        # Right column styles (optimized for one-page)
        self.styles.add(ParagraphStyle(
            name='RightColumnText',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=2,
            alignment=TA_JUSTIFY,
            leftIndent=0.15*inch  # Indent content under headers
        ))
        
        self.styles.add(ParagraphStyle(
            name='ExperienceTitle',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceBefore=4,
            spaceAfter=1,
            textColor=black,
            fontName='Helvetica-Bold',
            leftIndent=0.15*inch  # Indent content under headers
        ))
        
        self.styles.add(ParagraphStyle(
            name='ExperienceSubtitle',
            parent=self.styles['Normal'],
            fontSize=8,
            spaceAfter=2,
            textColor=darkgray,
            fontName='Helvetica-Oblique',
            leftIndent=0.15*inch  # Indent content under headers
        ))
    
    def generate_pdf(self, resume_data: ResumeData, output_path: str | Path) -> None:
        """Generate a PDF resume from ResumeData.
        
        Args:
            resume_data: The resume data model to convert to PDF.
            output_path: Path where the PDF should be saved.
        """
        output_path = Path(output_path)
        
        # Set up the document with column-aware overflow detection
        doc = ColumnAwareDoc(
            str(output_path),
            pagesize=letter,
            rightMargin=0.25*inch,
            leftMargin=0.25*inch,
            topMargin=0.25*inch,
            bottomMargin=0.25*inch
        )
        
        # Store document reference for left column marking
        self._current_doc = doc
        
        # Calculate column widths (34% / 66% split)
        page_width = letter[0] - doc.leftMargin - doc.rightMargin
        left_col_width = page_width * 0.34
        right_col_width = page_width * 0.66
        
        # Store column widths for use in section headers
        self.left_col_width = left_col_width - 0.1*inch  # Account for gap
        self.right_col_width = right_col_width - 0.1*inch  # Account for gap
        
        # Define frames for two-column layout
        left_frame = Frame(
            doc.leftMargin,
            doc.bottomMargin,
            left_col_width - 0.1*inch,  # Small gap between columns
            doc.height,
            id='left_col',
            showBoundary=0
        )
        
        right_frame = Frame(
            doc.leftMargin + left_col_width + 0.1*inch,
            doc.bottomMargin,
            right_col_width - 0.1*inch,
            doc.height,
            id='right_col',
            showBoundary=0
        )
        
        # Create page template with two frames and tinted left column
        template = TintedPageTemplate(
            id='TwoCol', 
            frames=[left_frame, right_frame],
            left_col_width=left_col_width,
            page_width=page_width,
            page_height=letter[1],  # Full page height
            left_margin=doc.leftMargin
        )
        doc.addPageTemplates([template])
        
        # Build content for both columns
        story = []
        
        # Add candidate header (spans both columns by being in left frame)
        story.extend(self._build_candidate_header(resume_data.candidate_info))
        story.append(Spacer(1, 0.1*inch))
        
        # Left column content
        story.extend(self._build_professional_summary_left(resume_data.professional_summary))
        story.extend(self._build_contact_info(resume_data.candidate_info))
        story.extend(self._build_skills_section(resume_data.skills))
        story.extend(self._build_education_section(resume_data.education))
        if resume_data.certifications:
            story.extend(self._build_certifications_section(resume_data.certifications))
        
        # Frame break to switch to right column
        story.extend(self._frame_break())
        
        # Right column content
        story.extend(self._build_experience_section(resume_data.work_experience))
        if resume_data.custom_sections:
            story.extend(self._build_custom_sections(resume_data.custom_sections))
        
        # Build the PDF
        doc.build(story)
    
    def _create_section_header(self, title: str, for_right_column: bool = False) -> list[Any]:
        """Create a section header with title and column-appropriate underline.
        
        Args:
            title: The section title text.
            for_right_column: If True, uses right column width and style, otherwise left column.
        """
        elements = []
        
        # Use appropriate style and width for the column
        if for_right_column:
            elements.append(Paragraph(title, self.styles['SectionHeader']))
            line_width = self.right_col_width - 0.15*inch  # Account for indentation
        else:
            elements.append(Paragraph(title, self.styles['LeftColumnHeader']))
            line_width = self.left_col_width - 0.15*inch  # Account for indentation
        
        # Create a horizontal line that fits within the column
        line_drawing = Drawing(line_width, 3)
        line = Line(0, 1, line_width, 1)
        line.strokeColor = black
        line.strokeWidth = 1
        line_drawing.add(line)
        elements.append(line_drawing)
        elements.append(Spacer(1, 0.02*inch))
        
        return elements
    
    def _frame_break(self) -> Any:
        """Create a frame break to move to the next column."""
        from reportlab.platypus.doctemplate import FrameBreak
        from reportlab.platypus.flowables import Flowable
        
        class LeftColumnFinishedMarker(Flowable):
            """Marker flowable that indicates intentional end of left column."""
            
            def __init__(self, doc_ref):
                super().__init__()
                self.doc_ref = doc_ref
                
            def wrap(self, availWidth, availHeight):
                # Mark left column as finished when this marker is processed
                if hasattr(self.doc_ref, 'mark_left_column_finished'):
                    self.doc_ref.mark_left_column_finished()
                return (0, 0)  # Takes no space
            
            def draw(self):
                pass  # Nothing to draw
        
        # Return the marker followed by frame break
        return [LeftColumnFinishedMarker(self._current_doc), FrameBreak()]
    
    def _build_candidate_header(self, candidate: CandidateInfo) -> list[Any]:
        """Build the candidate header section."""
        elements = []
        elements.append(Paragraph(candidate.name, self.styles['CandidateName']))
        elements.append(Paragraph(candidate.title, self.styles['CandidateTitle']))
        return elements
    
    def _build_contact_info(self, candidate: CandidateInfo) -> list[Any]:
        """Build the contact information section for left column."""
        elements = []
        elements.extend(self._create_section_header("CONTACT", for_right_column=False))
        
        # Use Symbola font specifically for icons
        def format_contact_line(icon: str, text: str) -> str:
            try:
                # Check if Symbola font is available
                pdfmetrics.getFont('Symbola')
                return f'<font name="Symbola">{icon}</font> {text}'
            except Exception:
                # Fallback to Unicode without specific font
                return f'{icon} {text}'
        
        contact_info = [
            format_contact_line("\U0001F4DE", candidate.phone),
            format_contact_line("\U0001F582", candidate.email)
        ]
        
        if candidate.address:
            contact_info.append(format_contact_line("\U0001F4CD", candidate.address))
        
        if candidate.website:
            contact_info.append(format_contact_line("\U0001F310", candidate.website))
        
        if candidate.linkedin:
            contact_info.append(format_contact_line("\U0001F310", "LinkedIn"))
        
        if candidate.github:
            contact_info.append(format_contact_line("\U0001F310", "GitHub"))
        
        if candidate.gitlab:
            contact_info.append(format_contact_line("\U0001F310", "GitLab"))
        
        for info in contact_info:
            elements.append(Paragraph(info, self.styles['LeftColumnText']))
        
        elements.append(Spacer(1, 0.05*inch))
        return elements
    
    def _build_professional_summary_left(self, summary: str) -> list[Any]:
        """Build the professional summary section for left column."""
        elements = []
        elements.append(Paragraph(summary, self.styles['LeftColumnSummary']))
        elements.append(Spacer(1, 0.05*inch))
        return elements
    
    def _build_skills_section(self, skills: dict[str, list[str]]) -> list[Any]:
        """Build the skills section for left column."""
        elements = []
        elements.extend(self._create_section_header("SKILLS", for_right_column=False))
        
        skill_categories = list(skills.items())
        for i, (category, skill_list) in enumerate(skill_categories):
            elements.append(Paragraph(f"<b>{category.upper()}</b>", self.styles['LeftColumnText']))
            skills_text = " • ".join(skill_list)
            elements.append(Paragraph(skills_text, self.styles['LeftColumnText']))
            
            # Add more space between categories, but not after the last one
            if i < len(skill_categories) - 1:
                elements.append(Spacer(1, 0.08*inch))
            else:
                elements.append(Spacer(1, 0.02*inch))
        
        elements.append(Spacer(1, 0.05*inch))
        return elements
    
    def _build_education_section(self, education: list[EducationBlock]) -> list[Any]:
        """Build the education section for left column."""
        elements = []
        elements.extend(self._create_section_header("EDUCATION", for_right_column=False))
        
        for edu in education:
            elements.append(Paragraph(f"<b>{edu.degree}</b>", self.styles['LeftColumnText']))
            elements.append(Paragraph(f"{edu.field_of_study}", self.styles['LeftColumnText']))
            elements.append(Paragraph(f"{edu.institution}", self.styles['LeftColumnText']))
            
            if edu.location:
                elements.append(Paragraph(f"{edu.location}", self.styles['LeftColumnText']))
            
            # Format dates
            end_date = edu.end_date.strftime("%Y") if edu.end_date else "Present"
            start_date = edu.start_date.strftime("%Y")
            elements.append(Paragraph(f"{start_date} - {end_date}", self.styles['LeftColumnText']))
            
            if edu.gpa:
                elements.append(Paragraph(f"GPA: {edu.gpa:.2f}", self.styles['LeftColumnText']))
            
            elements.append(Spacer(1, 0.05*inch))
        
        return elements
    
    def _build_certifications_section(self, certifications: list[CertificationBlock]) -> list[Any]:
        """Build the certifications section for left column."""
        elements = []
        elements.extend(self._create_section_header("CERTIFICATIONS", for_right_column=False))
        
        for cert in certifications:
            elements.append(Paragraph(f"<b>{cert.title}</b>", self.styles['LeftColumnText']))
            if cert.issuer:
                elements.append(Paragraph(f"{cert.issuer}", self.styles['LeftColumnText']))
            
            if cert.issue_date:
                issue_date = cert.issue_date.strftime("%Y")
                expiry_text = ""
                if cert.expiry_date:
                    expiry_date = cert.expiry_date.strftime("%Y")
                    expiry_text = f" - {expiry_date}"
                elements.append(Paragraph(f"{issue_date}{expiry_text}", self.styles['LeftColumnText']))
            
            elements.append(Spacer(1, 0.02*inch))
        
        return elements
    
    def _build_experience_section(self, experience: list) -> list[Any]:
        """Build the work experience section for right column."""
        elements = []
        elements.extend(self._create_section_header("WORK EXPERIENCE", for_right_column=True))
        
        for exp in experience:
            # Job title and company
            elements.append(Paragraph(f"{exp.position}", self.styles['ExperienceTitle']))
            
            # Company and dates
            end_date = exp.end_date.strftime("%b %Y") if exp.end_date else "Present"
            start_date = exp.start_date.strftime("%b %Y")
            company_info = f"{exp.company} | {start_date} - {end_date}"
            elements.append(Paragraph(company_info, self.styles['ExperienceSubtitle']))
            
            # Summary points
            if exp.summary:
                for point in exp.summary:
                    elements.append(Paragraph(f"• {point}", self.styles['RightColumnText']))
            
            elements.append(Spacer(1, 0.05*inch))
        
        return elements
    
    def _build_custom_sections(self, custom_sections: dict[str, list]) -> list[Any]:
        """Build custom sections for right column."""
        elements = []
        
        for section_title, blocks in custom_sections.items():
            elements.extend(self._create_section_header(section_title.upper(), for_right_column=True))
            
            for block in blocks:
                if hasattr(block, 'title'):
                    elements.append(Paragraph(f"<b>{block.title}</b>", self.styles['ExperienceTitle']))
                
                if hasattr(block, 'subtitle') and block.subtitle:
                    elements.append(Paragraph(block.subtitle, self.styles['ExperienceSubtitle']))
                
                if hasattr(block, 'summary') and block.summary:
                    for point in block.summary:
                        elements.append(Paragraph(f"• {point}", self.styles['RightColumnText']))
                
                elements.append(Spacer(1, 0.05*inch))
        
        return elements


def generate_resume_pdf(resume_data: ResumeData, output_path: str | Path) -> None:
    """Convenience function to generate a PDF resume.
    
    Args:
        resume_data: The resume data model to convert to PDF.
        output_path: Path where the PDF should be saved.
    """
    generator = ResumeGenerator()
    generator.generate_pdf(resume_data, output_path)