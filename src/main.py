import os
from core.parsing.parser import ResumeParser
from core.utils.config_manager import ConfigManager
import json

config = ConfigManager()
# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
resume_path = os.path.join(script_dir, config.settings.resume.input_path, f"{config.settings.resume.file_name}.docx")

resume_parser = ResumeParser(resume_path)
resume_text = resume_parser.parse_resume_sections()
with open(os.path.join(script_dir, config.settings.resume.output_path, f"{config.settings.resume.file_name}.json"), "w+") as f:
    json.dump(resume_text, f)
parsed_sections = resume_parser.parse_detailed_sections(resume_text)
with open(os.path.join(script_dir, config.settings.resume.output_path, f"{config.settings.resume.file_name}_detailed.json"), "w+") as f:
    json.dump(parsed_sections, f)