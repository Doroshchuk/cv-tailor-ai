from sys import path
from docx import Document
from .enums import ResumeSectionType
import json
import os
import re


class ResumeParser:
    def __init__(self, resume_path: str):
        self.resume_path = resume_path

        if not os.path.exists(resume_path):
            raise FileNotFoundError(f"Resume file not found: {resume_path}")

        if not resume_path.endswith('.docx'):
            raise ValueError(f"Unsupported file format. Expected '.docx' got {resume_path}")

    def parse_resume(self) -> str:
        try:
            doc = Document(self.resume_path)
            text = ""
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text + "\n"
            return text
        except Exception as e:
            print(f"Error parsing resume: {e}")
            return ""
    
    def _get_section_type(self, text: str) -> ResumeSectionType:
        """Map text to ResumeSectionType enum"""
        text_upper = text.strip().upper()
        for section_type in ResumeSectionType:
            if section_type.value == text_upper:
                return section_type
        return ResumeSectionType.HEADER  # default fallback
    
    def parse_resume_sections(self) -> dict[ResumeSectionType, list[str]]:
        try:
            doc = Document(self.resume_path)
            sections = {}
            current_section = ResumeSectionType.HEADER
            sections[current_section] = []

            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    if (paragraph.style and paragraph.style.name and paragraph.style.name.startswith("Heading")) or \
                    (len(paragraph.text.strip()) < 50 and paragraph.text.strip().isupper()):
                        current_section = self._get_section_type(paragraph.text)
                        if current_section not in sections:
                            sections[current_section] = []
                    else:
                        if current_section not in sections:
                            sections[current_section] = []
                        sections[current_section].append(paragraph.text.strip())

            return sections
        except Exception as e:
            print(f"Error parsing resume sections: {e}")
            return {}

    def _check_if_section_empty(self, section_text: list[str], section_type: ResumeSectionType) -> bool:
        if not section_text:
            print(f"Warning: {section_type.value} section is empty")
            return True
        return False

    def _safe_split(self, text_to_split: str, separator: str, max_splits: int = -1) -> list[str]:
        if separator in text_to_split:
            return text_to_split.split(separator, max_splits)
        return [text_to_split]

    def _clean_text_list(self, text_list: list[str]) -> list[str]:
        return [text.strip() for text in text_list if text.strip()]

    def _safe_get_and_strip(self, list: list[str], index: int, default_value: str = "") -> str:
        try:
            return list[index].strip()
        except IndexError:
            return default_value

    def _validate_required_fields(self, parsed_data: dict, required_fields: list[str], section_type: ResumeSectionType) -> bool:
        missing_fields = [field for field in required_fields if not parsed_data.get(field)]
        if missing_fields:
            print(f"Warning: Missing required fields: {missing_fields}")
            return False
        return True

    def parse_resume_header(self, header_text: list[str]) -> dict[str, str]:
        if not header_text or len(header_text) < 4:
            print("Warning: Header section has insufficient data")
            return {}

        parsed_header = {}
        try :
            parsed_header["name"] = header_text[0]
            parsed_header["location"] = header_text[1]
            contact_info = header_text[2]
            if " ∙ " in contact_info:
                contact_info_parts = self._safe_split(contact_info, " ∙ ")
                parsed_header["phone"] = self._safe_get_and_strip(contact_info_parts, 0)
                parsed_header["email"] = self._safe_get_and_strip(contact_info_parts, 1)
            else:
                parsed_header["phone"] = contact_info.strip()
                parsed_header["email"] = None
            # parse LinkedIn, GitHub links
            parsed_header["work_authorized"] = header_text[3]
            
            if not self._validate_required_fields(parsed_header, ["name", "location", "phone", "email", "work_authorized"], ResumeSectionType.HEADER):
                return {}

            return parsed_header
        except IndexError as e:
            print(f"Error parsing header: {e}")
            return {}

    def parse_resume_professional_summary(self, professional_summary_text: list[str]) -> dict[str, str]:
        if self._check_if_section_empty(professional_summary_text, ResumeSectionType.PROFESSIONAL_SUMMARY):
            return {}
        
        parsed_professional_summary = {}
        try:
            parsed_professional_summary["summary"] = self._safe_get_and_strip(professional_summary_text, 0)
            parsed_professional_summary["highlights"] = professional_summary_text[1:]

            if not self._validate_required_fields(parsed_professional_summary, ["summary", "highlights"], ResumeSectionType.PROFESSIONAL_SUMMARY):
                return {}

            return parsed_professional_summary
        except IndexError as e:
            print(f"Error parsing professional summary: {e}")
            return {}
    
    def parse_resume_technical_skills(self, technical_skills_text: list[str]) -> dict[str, str]:
        if self._check_if_section_empty(technical_skills_text, ResumeSectionType.TECHNICAL_SKILLS):
            return {}

        parsed_technical_skills = {}
        parsed_technical_skills["skills"] = self._clean_text_list(technical_skills_text)
        return parsed_technical_skills

    def _get_supported_positions(self) -> list[str]:
        positions = []
        script_dir = os.path.dirname(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
        try:
            with open(os.path.join(script_dir, "configs/positions.json"), "r") as f:
                roles = dict(json.load(f))
                for role in roles:
                    positions.extend(roles[role]["aliases"])
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Positions config file not found: {e}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Error parsing positions.config: {e}", e.doc, e.pos)
        return positions

    def parse_resume_professional_experience(self, experience_list: list[str]) -> list[dict]:
        if not experience_list:
            print("Warning: Education section is empty")
            return []
        
        experience_text = "\n".join(experience_list)
        positions = self._get_supported_positions()
        parsed_experience = []

         # Regex to find each position and its start line
        position_pattern = re.compile(rf"({'|'.join(map(re.escape, positions))})\s+(\d{{2}}/\d{{4}}.*?)\n")
        matches = list(position_pattern.finditer(experience_text))
        for i, match in enumerate(matches):
            position = match.group(1).strip()
            dates = match.group(2).strip()

            # Capture block of experience text
            start_idx = match.end()
            end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(experience_text)
            block = experience_text[start_idx:end_idx].strip()
            lines = block.splitlines()

            if len(lines) < 3:
                print(f"Warning: Experience block has insufficient data: {block}")
                continue

            if "|" in lines[0]:
                company_parts = self._safe_split(lines[0], "|")
                company = self._safe_get_and_strip(company_parts, 0)
                location = self._safe_get_and_strip(company_parts, 1)
            else:
                company = self._safe_get_and_strip(lines, 0)
                location = None
            
            company_description = self._safe_get_and_strip(lines, 1)
            project_description = self._safe_get_and_strip(lines, 2) if lines[2].startswith("Project") else None
            bullet_lines = lines[2:] if not project_description else lines[3:]

            # Clean and collect bullets
            bullets = self._clean_text_list(bullet_lines)

            experience = {
                "position": position,
                "dates": dates,
                "company": company,
                "location": location,
                "company_description": company_description,
                "project_description": project_description,
                "bullets": bullets
            }
            parsed_experience.append(experience)
        return parsed_experience

    def parse_resume_education(self, education_text: list[str]) -> dict[str, str]:
        if self._check_if_section_empty(education_text, ResumeSectionType.EDUCATION):
            return {}

        parsed_education = {}
        try:
            university_line = education_text[0]
            if "," in university_line:
                parts = self._safe_split(university_line, ",")
                parsed_education["university"] = self._safe_get_and_strip(parts, 0)
                parsed_education["country"] = self._safe_get_and_strip(parts, 1)
            else:
                parsed_education["university"] = university_line.strip()
                parsed_education["country"] = ""
                
            degrees = []
            for raw in education_text[1:]:
                degree = {}
                raw_parts = self._safe_split(raw, ",")
                if len(raw_parts) == 3:
                    degree["degree"] = self._safe_get_and_strip(raw_parts, 0)
                    degree["field_of_study"] = self._safe_get_and_strip(raw_parts, 1)
                    degree["year_of_graduation"] = self._safe_get_and_strip(raw_parts, 2)
                else:
                    degree["degree"] = raw.strip()
                    degree["field_of_study"] = ""
                    degree["year_of_graduation"] = ""
                degrees.append(degree)
            parsed_education["degrees"] = degrees
            return parsed_education
        except IndexError as e:
            print(f"Error parsing education: {e}")
            return {}
    
    def parse_resume_professional_development(self, professional_development_text: list[str]) -> dict[str, str]:
        if self._check_if_section_empty(professional_development_text, ResumeSectionType.PROFESSIONAL_DEVELOPMENT_OR_AFFILIATIONS):
            return {}
        
        parsed_professional_development = {}
        parsed_professional_development["projects_or_certifications"] = self._clean_text_list(professional_development_text)
        return parsed_professional_development

    def parse_detailed_sections(self, sections: dict[ResumeSectionType, list[str]]) -> dict:
        parsed_sections = {}
        for section_type, section_text in sections.items():
            if section_type == ResumeSectionType.HEADER:
                parsed_sections[section_type] = self.parse_resume_header(section_text)
            elif section_type == ResumeSectionType.PROFESSIONAL_SUMMARY:
                parsed_sections[section_type] = self.parse_resume_professional_summary(section_text)
            elif section_type == ResumeSectionType.TECHNICAL_SKILLS:
                parsed_sections[section_type] = self.parse_resume_technical_skills(section_text)
            elif section_type == ResumeSectionType.PROFESSIONAL_EXPERIENCE:
                parsed_sections[section_type] = self.parse_resume_professional_experience(section_text)
            elif section_type == ResumeSectionType.EDUCATION:
                parsed_sections[section_type] = self.parse_resume_education(section_text)
            elif section_type == ResumeSectionType.PROFESSIONAL_DEVELOPMENT_OR_AFFILIATIONS:
                parsed_sections[section_type] = self.parse_resume_professional_development(section_text)
            else:
                parsed_sections[section_type] = section_text
        return parsed_sections     
