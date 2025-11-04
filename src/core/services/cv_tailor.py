from core.services.config_manager import ConfigManager
from core.services.openai_client import OpenAIClient
import core.utils.paths as path_utils
from core.utils.helpers import PromptParserUtils, KeywordUtils
from core.utils.log_helper import LogHelper
from core.models.resume import Resume, ResumeLite, TailoredResumeLite
from core.models.prompt_instructions import Keyword
from core.models.jobscan_match_report import SkillType
from core.models.job_to_target import JobDetails
import json

class TailorAIService:
    def __init__(self, job_description: JobDetails):
        self.config = ConfigManager()
        self.logger = LogHelper("openai_client")
        self.job_description = job_description
        api_key = self.config.get_openai_api_key()
        if not api_key:
            error = "OpenAI api key is missing"
            self.logger.error(error)
            raise ValueError(error)
        self.openai_client = OpenAIClient(api_key)
        self.prompt_instructions = PromptParserUtils.parse_prompt_instructions(path_utils.get_prompt_instructions_file_path(), self.logger)

    def tailor_cv(self, resume: Resume, keywords: dict[SkillType, list[Keyword]]) -> TailoredResumeLite:
        system: str = self.prompt_instructions.get_system_instructions()
        task: str = self.prompt_instructions.get_task_instructions()
        resume_lite: ResumeLite = resume.get_lite_version()

        user = f"""
        JOB DESCRIPTION:
        {str(self.job_description)}

        KEYWORD REQUIREMENTS:
        {KeywordUtils.keywords_to_json(keywords)}

        CURRENT RESUME (JSON):
        {json.dumps(resume_lite.model_dump(mode="json"))}

        TASK:
        {task}
        """

        result = self.openai_client.request_openai(
            {
                "system": system,
                "user": user
            }
        )

        if isinstance(result, str):
            data = json.loads(result)
        elif isinstance(result, dict):
            data = result
        else:
            raise TypeError("result must be JSON str or dict")

        return TailoredResumeLite.model_validate(data)




