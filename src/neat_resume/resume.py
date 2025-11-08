# SPDX-FileCopyrightText: 2025-present Ricardo Rivera <silkrad@ririlabs.com>
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from datetime import date

import pydantic
import phonenumbers
from pydantic import EmailStr, HttpUrl
from pydantic_extra_types.phone_numbers import PhoneNumber


class CandidateInfo(pydantic.BaseModel):
    address: str | None = pydantic.Field(default=None, description="Physical address or location", frozen=True)
    email: EmailStr = pydantic.Field(description="Contact email address", frozen=True)
    github: HttpUrl | None = pydantic.Field(default=None, description="GitHub profile URL", frozen=True)
    gitlab: HttpUrl | None = pydantic.Field(default=None, description="GitLab profile URL", frozen=True)
    linkedin: HttpUrl | None = pydantic.Field(default=None, description="LinkedIn profile URL", frozen=True)
    name: str = pydantic.Field(description="Full name", frozen=True)
    phone: PhoneNumber = pydantic.Field(description="Contact phone number", frozen=True)
    title: str = pydantic.Field(description="Professional title or job title", frozen=True)
    website: HttpUrl | None = pydantic.Field(default=None, description="Personal website URL", frozen=True)

    @property
    def phone_regional(self) -> str:
        parsed = phonenumbers.parse(self.phone)
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)


class ExperienceBlock(pydantic.BaseModel):
    company: str = pydantic.Field(description="Name of the company or organization", frozen=True)
    end_date: date | None = pydantic.Field(default=None, description="End date of the role", frozen=True)
    location: str | None = pydantic.Field(default=None, description="Location of the role", frozen=True)
    position: str = pydantic.Field(description="Job title or position held", frozen=True)
    start_date: date = pydantic.Field(description="Start date of the role", frozen=True)
    summary: list[str] = pydantic.Field(description="List of key responsibilities or achievements in the role", frozen=True)


class SectionBlock(pydantic.BaseModel):
    end_date: date | None = pydantic.Field(default=None, description="End date associated with the section", frozen=True)
    location: str | None = pydantic.Field(default=None, description="Location associated with the section", frozen=True)
    start_date: date | None = pydantic.Field(default=None, description="Start date associated with the section", frozen=True)
    subtitle: str | None = pydantic.Field(default=None, description="Subtitle of the custom section", frozen=True)
    summary: list[str] = pydantic.Field(description="List of strings representing the content of the section", frozen=True)
    title: str = pydantic.Field(description="Title of the custom section", frozen=True)


class RecognitionBlock(pydantic.BaseModel):
    issue_date: date | None = pydantic.Field(default=None, description="Date when the recognition was issued", frozen=True)
    name: str = pydantic.Field(description="Name or title of the recognition or credential", frozen=True)


class EducationBlock(pydantic.BaseModel):
    degree: str = pydantic.Field(description="Degree or qualification obtained", frozen=True)
    end_date: date | None = pydantic.Field(default=None, description="End date of the education", frozen=True)
    gpa: float | None = pydantic.Field(default=None, ge=0, le=4, description="Grade point average (GPA)", frozen=True)
    institution: str = pydantic.Field(description="Name of the educational institution", frozen=True)
    location: str = pydantic.Field(description="Location of the educational institution", frozen=True)
    start_date: date | None = pydantic.Field(default=None, description="Start date of the education", frozen=True)
    summary: list[str] = pydantic.Field(description="List of key highlights or achievements during the education", frozen=True)


class SectionNames(pydantic.BaseModel):
    recognitions: str = pydantic.Field(default="Recognitions", description="Name of the recognitions section", frozen=True)
    contact: str = pydantic.Field(default="Contact", description="Name of the contact information section", frozen=True)
    education: str = pydantic.Field(default="Education", description="Name of the education section", frozen=True)
    experience: str = pydantic.Field(default="Professional Experience", description="Name of the experience section", frozen=True)
    skills: str = pydantic.Field(default="Skills", description="Name of the skills section", frozen=True)


class Resume(pydantic.BaseModel):
    candidate: CandidateInfo = pydantic.Field(description="Candidate personal and contact details", frozen=True)
    recognitions: list[RecognitionBlock] = pydantic.Field(default_factory=list, description="List of recognition blocks", frozen=True)
    education: list[EducationBlock] = pydantic.Field(default_factory=list, description="List of educational background blocks", frozen=True)
    experience: list[ExperienceBlock] = pydantic.Field(default_factory=list, description="List of work experience blocks", frozen=True)
    skills: dict[str, list[str]] = pydantic.Field(default_factory=dict, description="List of candidate skills", frozen=True)
    sections: dict[str, list[SectionBlock]] = pydantic.Field(default_factory=dict, description="Mapping of titles to sections", frozen=True)
    section_names: SectionNames = pydantic.Field(default_factory=SectionNames, description="Standardized section names", frozen=True)
    summary: str = pydantic.Field(description="Brief professional summary or objective statement", frozen=True)
