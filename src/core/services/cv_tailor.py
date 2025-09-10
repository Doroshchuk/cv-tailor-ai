from core.services.config_manager import ConfigManager
from core.services.openai_client import OpenAIClient
import core.utils.paths as path_utils
from core.utils.helpers import PromptParserUtils
from core.utils.log_helper import LogHelper
from core.models.resume import Resume, ResumeLite, TailoredResumeLite
from core.models.prompt_instructions import Keyword
from core.models.jobscan_match_report import SkillType
from core.models.job_to_target import JobDetails
import json

class TailorAIService:
    def __init__(self, job_description: JobDetails):
        self.config = ConfigManager()
        self.logger = LogHelper("cv_tailor_service")
        self.job_description = job_description
        self.openai_client = OpenAIClient(self.config.get_openai_api_key())
        self.prompt_instructions = PromptParserUtils.parse_prompt_instructions(path_utils.get_prompt_instructions_file_path(), self.logger)

    def tailor_cv(self, resume: Resume, keywords: dict[SkillType, list[Keyword]]) -> TailoredResumeLite:
        tailored_resume_schema: dict = TailoredResumeLite.model_json_schema()
        system: str = self.prompt_instructions.get_system_instructions()
        task: str = self.prompt_instructions.get_task_instructions()
        resume_lite: ResumeLite = resume.get_lite_version()

        user = f"""
        JOB DESCRIPTION:
        {str(self.job_description)}

        KEYWORD REQUIREMENTS:
        {json.dumps(keywords)}

        CURRENT RESUME (JSON):
        {json.dumps(resume_lite.model_dump(mode="json"))}

        TASK:
        {task}
        """

        result = self.openai_client.request_openai(
            {
                "system": system,
                "user": user
            },
            response_format={"type": "json_schema", "json_schema": tailored_resume_schema}
        )
        if isinstance(result, str):
            data = json.loads(result)
        elif isinstance(result, dict):
            data = result
        else:
            raise TypeError("result must be JSON str or dict")

        return TailoredResumeLite.model_validate(data)




