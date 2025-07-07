from docx import Document
from .enums import ResumeSectionType


class ResumeParser:
    def __init__(self, resume_path: str):
        self.resume_path = resume_path

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