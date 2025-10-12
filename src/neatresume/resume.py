# SPDX-FileCopyrightText: 2025-present Ricardo Rivera <silkrad@ririlabs.com>
#
# SPDX-License-Identifier: Apache-2.0

"""Resume data models for the neatresume package.

This module defines Pydantic models for representing resume and candidate information
with robust validation and type checking.
"""

from __future__ import annotations

from datetime import date
import pydantic
from pydantic import EmailStr, HttpUrl, Field
from pydantic_extra_types.phone_numbers import PhoneNumber


class CandidateInfo(pydantic.BaseModel):
    """Represent immutable job candidate information with validated contact details and online profiles.

    This model validates candidate data including required contact details
    and optional social media/professional profiles using specialized
    Pydantic types for robust validation. All fields are frozen to ensure
    immutability after creation.

    Attributes:
        email: Contact email address with validation (required, immutable).
        name: Full name of the candidate (required, immutable).
        phone: Contact phone number with international validation (required, immutable).
        title: Professional title or job title (required, immutable).
        address: Physical address or location (optional, immutable).
        github: GitHub profile URL with validation (optional, immutable).
        gitlab: GitLab profile URL with validation (optional, immutable).
        linkedin: LinkedIn profile URL with validation (optional, immutable).
        website: Personal website URL with validation (optional, immutable).
    """

    # Required fields
    email: EmailStr = Field(description="Contact email address", frozen=True)
    name: str = Field(description="Full name", frozen=True)
    phone: PhoneNumber = Field(description="Contact phone number", frozen=True)
    title: str = Field(description="Professional title or job title", frozen=True)

    # Optional fields
    address: str | None = Field(default=None, description="Physical address or location", frozen=True)
    github: HttpUrl | None = Field(default=None, description="GitHub profile URL", frozen=True)
    gitlab: HttpUrl | None = Field(default=None, description="GitLab profile URL", frozen=True)
    linkedin: HttpUrl | None = Field(default=None, description="LinkedIn profile URL", frozen=True)
    website: HttpUrl | None = Field(default=None, description="Personal website URL", frozen=True)


class ExperienceBlock(pydantic.BaseModel):
    """Represent an immutable block of work experience in a resume.

    This model captures details about a specific job or role held by the candidate,
    including the company, position, duration, and key responsibilities or achievements.
    All fields are frozen to ensure immutability after creation.

    Attributes:
        company: Name of the company or organization (required, immutable).
        position: Job title or position held (required, immutable).
        start_date: Start date of the role as a date object (required, immutable).
        summary: List of key responsibilities or achievements (required, immutable).
        end_date: End date of the role as a date object, or None if currently employed (optional, immutable).
    """

    # Required fields
    company: str = Field(description="Name of the company or organization", frozen=True)
    position: str = Field(description="Job title or position held", frozen=True)
    start_date: date = Field(description="Start date of the role", frozen=True)
    summary: list[str] = Field(description="List of key responsibilities or achievements in the role", frozen=True)

    # Optional fields
    end_date: date | None = Field(default=None, description="End date of the role", frozen=True)


class CustomBlock(pydantic.BaseModel):
    """Represent an immutable custom section in a resume.

    This model captures additional custom sections that may be included
    in a resume, such as projects, certifications, awards, publications,
    volunteer work, or other relevant information. All fields are frozen
    to ensure immutability after creation.

    Attributes:
        summary: List of strings representing the content of the section (required, immutable).
        title: Title of the custom section (required, immutable).
        end_date: End date associated with the section as a date object (optional, immutable).
        location: Location associated with the section (optional, immutable).
        start_date: Start date associated with the section as a date object (optional, immutable).
        subtitle: Subtitle of the custom section (optional, immutable).
    """

    # Required fields
    summary: list[str] = Field(description="List of strings representing the content of the section", frozen=True)
    title: str = Field(description="Title of the custom section", frozen=True)

    # Optional fields
    end_date: date | None = Field(default=None, description="End date associated with the section", frozen=True)
    location: str | None = Field(default=None, description="Location associated with the section", frozen=True)
    start_date: date | None = Field(default=None, description="Start date associated with the section", frozen=True)
    subtitle: str | None = Field(default=None, description="Subtitle of the custom section", frozen=True)


class CertificationBlock(pydantic.BaseModel):
    """Represent an immutable certification or credential in a resume.

    This model captures essential details about a professional certification or
    credential obtained by the candidate. All fields are frozen to ensure
    immutability after creation.

    Attributes:
        issue_date: Date when the certification was issued (required, immutable).
        title: Name or title of the certification or credential (required, immutable).
    """

    # Required fields
    issue_date: date = Field(description="Date when the certification was issued", frozen=True)
    title: str = Field(description="Name or title of the certification or credential", frozen=True)


class EducationBlock(pydantic.BaseModel):
    """Represent an immutable block of educational background in a resume.

    This model captures details about a specific educational qualification or degree
    obtained by the candidate, including the institution, degree, field of study,
    location, duration, and key highlights. All fields are frozen to ensure
    immutability after creation.

    Attributes:
        degree: Degree or qualification obtained (required, immutable).
        field_of_study: Field of study or major (required, immutable).
        institution: Name of the educational institution (required, immutable).
        location: Location of the educational institution (required, immutable).
        start_date: Start date of the education as a date object (required, immutable).
        summary: List of key highlights or achievements during the education (required, immutable).
        end_date: End date of the education as a date object, or None if currently enrolled (optional, immutable).
        gpa: Grade point average on a 0-4 scale (optional, immutable).
    """

    # Required fields
    degree: str = Field(description="Degree or qualification obtained", frozen=True)
    field_of_study: str = Field(description="Field of study or major", frozen=True)
    institution: str = Field(description="Name of the educational institution", frozen=True)
    location: str = Field(description="Location of the educational institution", frozen=True)
    start_date: date = Field(description="Start date of the education", frozen=True)
    summary: list[str] = Field(description="List of key highlights or achievements during the education", frozen=True)

    # Optional fields
    end_date: date | None = Field(default=None, description="End date of the education", frozen=True)
    gpa: float | None = Field(default=None, ge=0, le=4, description="Grade point average (GPA)", frozen=True)

class Resume(pydantic.BaseModel):
    """Represent an immutable comprehensive resume with all candidate information and sections.

    This model encapsulates all essential and optional sections of a professional resume,
    including candidate contact information, professional summary, skills categorized by type,
    work experience history, educational background, certifications, and flexible custom 
    sections. All fields are frozen to ensure immutability after creation.

    Attributes:
        candidate_info: CandidateInfo model containing personal and contact details (required, immutable).
        education: List of EducationBlock models representing educational background (required, immutable).
        professional_summary: Brief professional summary or objective statement (required, immutable).
        skills: Dictionary mapping skill categories to lists of specific skills (required, immutable).
        work_experience: List of ExperienceBlock models representing work history (required, immutable).
        certifications: List of CertificationBlock models representing certifications obtained (optional, immutable).
        custom_sections: Dictionary mapping custom section titles to lists of CustomBlock models (optional, immutable).
    """

    # Required fields (alphabetically sorted)
    candidate_info: CandidateInfo = Field(description="Candidate personal and contact details", frozen=True)
    education: list[EducationBlock] = Field(description="List of educational background blocks", frozen=True)
    professional_summary: str = Field(description="Brief professional summary or objective statement", frozen=True)
    skills: dict[str, list[str]] = Field(description="Dictionary mapping skill categories to lists of specific skills", frozen=True)
    work_experience: list[ExperienceBlock] = Field(description="List of work experience blocks", frozen=True)

    # Optional fields (alphabetically sorted)
    certifications: list[CertificationBlock] | None = Field(default=None, description="List of certification blocks", frozen=True)
    custom_sections: dict[str, list[CustomBlock]] | None = Field(default=None, description="Dictionary mapping custom section titles to lists of custom blocks", frozen=True)
