#!/usr/bin/env python3
"""Simple JSON-to-PDF resume generator.

This script loads resume data from a JSON file and generates a PDF resume.
It's a streamlined version focused on JSON input processing.
"""

import json
import sys
from pathlib import Path

from src.neatresume.resume_data import ResumeData
from src.neatresume.generator import generate_resume_pdf


def load_resume_from_json(json_path: str | Path) -> ResumeData:
    """Load and validate resume data from a JSON file.
    
    Args:
        json_path: Path to the JSON file containing resume data.
        
    Returns:
        ResumeData: Validated resume data model.
    """
    json_path = Path(json_path)
    
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")
    
    # Load JSON data
    with json_path.open('r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # Parse and validate using Pydantic
    resume_data = ResumeData.model_validate(json_data)
    
    return resume_data


def main() -> None:
    """Main function for JSON-to-PDF conversion."""
    # Default to Alex Chen's resume if no argument provided
    json_file = "alex_chen_resume.json"
    
    # Allow command line argument for JSON file
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    
    json_path = Path(json_file)
    
    print(f"🚀 Converting {json_path.name} to PDF...")
    
    try:
        # Load and validate JSON data
        print(f"📄 Loading resume data from {json_path}...")
        resume_data = load_resume_from_json(json_path)
        
        # Generate output filename from candidate name
        candidate_name = resume_data.candidate_info.name.lower().replace(" ", "_")
        output_file = Path(f"{candidate_name}_resume.pdf")
        
        print(f"✅ Successfully loaded resume for {resume_data.candidate_info.name}")
        print(f"🎨 Generating PDF: {output_file}...")
        
        # Generate PDF
        generate_resume_pdf(resume_data, output_file)
        
        print(f"✅ PDF generated successfully!")
        print(f"   File: {output_file}")
        print(f"   Size: {output_file.stat().st_size:,} bytes")
        
        # Show summary
        print(f"\n📊 Resume Summary:")
        print(f"   • Title: {resume_data.candidate_info.title}")
        print(f"   • Work Experience: {len(resume_data.work_experience)} positions")
        print(f"   • Education: {len(resume_data.education)} entries")
        print(f"   • Skills: {len(resume_data.skills)} categories")
        if resume_data.certifications:
            print(f"   • Certifications: {len(resume_data.certifications)} entries")
        if resume_data.custom_sections:
            print(f"   • Custom Sections: {len(resume_data.custom_sections)} sections")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print(f"   Available JSON files:")
        json_files = list(Path(".").glob("*.json"))
        for file in json_files:
            print(f"   - {file.name}")
        sys.exit(1)
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON Parse Error: {e}")
        print(f"   The file {json_path} contains invalid JSON.")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()