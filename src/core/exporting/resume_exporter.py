from core.models.resume import ResumeLite
from docxtpl import DocxTemplate
from pathlib import Path
import core.utils.paths as path_utils
import subprocess


class ResumeExporter:
    def __init__(self) -> None:
        self.template_path = path_utils.get_resume_template_file_path()

    def export(self, resume: ResumeLite, company: str, job_title: str) -> Path:
        template = DocxTemplate(self.template_path)
        ctx = resume.model_dump(mode="json")  # Pydantic v2 → JSON-safe dict
        template.render(ctx)
        tailored_resume_file_path = path_utils.get_tailored_resume_file_path(company, job_title, path_utils.FileFormat.DOCX)
        tailored_resume_file_path.parent.mkdir(parents=True, exist_ok=True)
        template.save(tailored_resume_file_path)
        return tailored_resume_file_path

    def docx_to_pdf(self, docx_path: Path) -> Path:
        pdf_path = docx_path.with_suffix(".pdf")
        subprocess.run(
            [
                "soffice",
                "--headless",
                "--convert-to", "pdf",
                "--outdir", str(docx_path.parent),
                str(docx_path)
            ],
            check=True
        )
        return pdf_path