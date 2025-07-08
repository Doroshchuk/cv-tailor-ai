import os
from cv_toolkit.parser import ResumeParser
import json

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
resume_path = os.path.join(script_dir, "resumes", "original", "Daria_Doroshchuk_MS_SDET.docx")

resume_parser = ResumeParser(resume_path)
resume_text = resume_parser.parse_resume_sections()
with open(os.path.join(script_dir, "resumes", "parsed","Daria_Doroshchuk_MS_SDET.json"), "w+") as f:
    json.dump(resume_text, f)
parsed_sections = resume_parser.parse_detailed_sections(resume_text)
with open(os.path.join(script_dir, "resumes", "parsed", "Daria_Doroshchuk_MS_SDET_detailed.json"), "w+") as f:
    json.dump(parsed_sections, f)
print(parsed_sections)