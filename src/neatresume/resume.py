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
import phonenumbers
from pydantic import EmailStr, HttpUrl
from pydantic_extra_types.phone_numbers import PhoneNumber


class CandidateInfo(pydantic.BaseModel):
    """Represent immutable job candidate information with validated contact details and online profiles.

    This model validates candidate data including required contact details
    and optional social media/professional profiles using specialized
    Pydantic types for robust validation. All pydantic.Fields are frozen to ensure
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

    email: EmailStr = pydantic.Field(description="Contact email address", frozen=True)
    name: str = pydantic.Field(description="Full name", frozen=True)
    phone: PhoneNumber = pydantic.Field(description="Contact phone number", frozen=True)
    title: str = pydantic.Field(description="Professional title or job title", frozen=True)

    address: str | None = pydantic.Field(default=None, description="Physical address or location", frozen=True)
    github: HttpUrl | None = pydantic.Field(default=None, description="GitHub profile URL", frozen=True)
    gitlab: HttpUrl | None = pydantic.Field(default=None, description="GitLab profile URL", frozen=True)
    linkedin: HttpUrl | None = pydantic.Field(default=None, description="LinkedIn profile URL", frozen=True)
    website: HttpUrl | None = pydantic.Field(default=None, description="Personal website URL", frozen=True)

    @pydantic.computed_field
    @property
    def phone_regional(self) -> str:
        parsed = phonenumbers.parse(self.phone)
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)


class ExperienceBlock(pydantic.BaseModel):
    """Represent an immutable block of work experience in a resume.

    This model captures details about a specific job or role held by the candidate,
    including the company, position, duration, and key responsibilities or achievements.
    All pydantic.Fields are frozen to ensure immutability after creation.

    Attributes:
        company: Name of the company or organization (required, immutable).
        position: Job title or position held (required, immutable).
        start_date: Start date of the role as a date object (required, immutable).
        summary: List of key responsibilities or achievements (required, immutable).
        end_date: End date of the role as a date object, or None if currently employed (optional, immutable).
    """

    company: str = pydantic.Field(description="Name of the company or organization", frozen=True)
    position: str = pydantic.Field(description="Job title or position held", frozen=True)
    start_date: date = pydantic.Field(description="Start date of the role", frozen=True)
    summary: list[str] = pydantic.Field(description="List of key responsibilities or achievements in the role", frozen=True)

    end_date: date | None = pydantic.Field(default=None, description="End date of the role", frozen=True)


class SectionBlock(pydantic.BaseModel):
    """Represent an immutable custom section in a resume.

    This model captures additional custom sections that may be included
    in a resume, such as projects, certifications, awards, publications,
    volunteer work, or other relevant information. All pydantic.Fields are frozen
    to ensure immutability after creation.

    Attributes:
        summary: List of strings representing the content of the section (required, immutable).
        title: Title of the custom section (required, immutable).
        end_date: End date associated with the section as a date object (optional, immutable).
        location: Location associated with the section (optional, immutable).
        start_date: Start date associated with the section as a date object (optional, immutable).
        subtitle: Subtitle of the custom section (optional, immutable).
    """

    summary: list[str] = pydantic.Field(description="List of strings representing the content of the section", frozen=True)
    title: str = pydantic.Field(description="Title of the custom section", frozen=True)

    end_date: date | None = pydantic.Field(default=None, description="End date associated with the section", frozen=True)
    location: str | None = pydantic.Field(default=None, description="Location associated with the section", frozen=True)
    start_date: date | None = pydantic.Field(default=None, description="Start date associated with the section", frozen=True)
    subtitle: str | None = pydantic.Field(default=None, description="Subtitle of the custom section", frozen=True)


class CertificationBlock(pydantic.BaseModel):
    """Represent an immutable certification or credential in a resume.

    This model captures essential details about a professional certification or
    credential obtained by the candidate. All pydantic.Fields are frozen to ensure
    immutability after creation.

    Attributes:
        title: Name or title of the certification or credential (required, immutable).
        issue_date: Date when the certification was issued (optional, immutable).
    """

    title: str = pydantic.Field(description="Name or title of the certification or credential", frozen=True)

    issue_date: date | None = pydantic.Field(default=None, description="Date when the certification was issued", frozen=True)


class EducationBlock(pydantic.BaseModel):
    """Represent an immutable block of educational background in a resume.

    This model captures details about a specific educational qualification or degree
    obtained by the candidate, including the institution, degree, pydantic.Field of study,
    location, duration, and key highlights. All pydantic.Fields are frozen to ensure
    immutability after creation.

    Attributes:
        degree: Degree or qualification obtained (required, immutable).
        pydantic.Field_of_study: pydantic.Field of study or major (required, immutable).
        institution: Name of the educational institution (required, immutable).
        location: Location of the educational institution (required, immutable).
        start_date: Start date of the education as a date object (required, immutable).
        summary: List of key highlights or achievements during the education (required, immutable).
        end_date: End date of the education as a date object, or None if currently enrolled (optional, immutable).
        gpa: Grade point average on a 0-4 scale (optional, immutable).
    """

    degree: str = pydantic.Field(description="Degree or qualification obtained", frozen=True)
    field_of_study: str = pydantic.Field(description="pydantic.Field of study or major", frozen=True)
    institution: str = pydantic.Field(description="Name of the educational institution", frozen=True)
    location: str = pydantic.Field(description="Location of the educational institution", frozen=True)
    start_date: date = pydantic.Field(description="Start date of the education", frozen=True)
    summary: list[str] = pydantic.Field(description="List of key highlights or achievements during the education", frozen=True)

    end_date: date | None = pydantic.Field(default=None, description="End date of the education", frozen=True)
    gpa: float | None = pydantic.Field(default=None, ge=0, le=4, description="Grade point average (GPA)", frozen=True)


class Resume(pydantic.BaseModel):
    """Represent an immutable comprehensive resume with all candidate information and sections.

    This model encapsulates all essential and optional sections of a professional resume,
    including candidate contact information, professional summary, skills categorized by type,
    work experience history, educational background, certifications, and flexible custom
    sections. All pydantic.Fields are frozen to ensure immutability after creation.

    Attributes:
        candidate: CandidateInfo model containing personal and contact details (required, immutable).
        education: List of EducationBlock models representing educational background (required, immutable).
        experience: List of ExperienceBlock models representing work history (required, immutable).
        skills: Dictionary mapping skill categories to lists of specific skills (required, immutable).
        summary: Brief professional summary or objective statement (required, immutable).
        certifications: List of CertificationBlock models representing certifications obtained (optional, immutable).
        sections: Dictionary mapping section titles to lists of SectionBlock models (optional, immutable).
    """

    candidate: CandidateInfo = pydantic.Field(description="Candidate personal and contact details", frozen=True)
    education: list[EducationBlock] = pydantic.Field(description="List of educational background blocks", frozen=True)
    experience: list[ExperienceBlock] = pydantic.Field(description="List of work experience blocks", frozen=True)
    skills: dict[str, list[str]] = pydantic.Field(description="Mapping of skill categories to lists of specific skills", frozen=True)
    summary: str = pydantic.Field(description="Brief professional summary or objective statement", frozen=True)

    certifications: list[CertificationBlock] = pydantic.Field(default_factory=list, description="List of certification blocks", frozen=True)
    sections: dict[str, list[SectionBlock]] = pydantic.Field(default_factory=dict, description="Mapping of titles to sections", frozen=True)
