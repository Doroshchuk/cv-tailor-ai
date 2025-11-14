from pydantic import BaseModel


class JobDetails(BaseModel):
    url: str
    title: str
    company: str
    description_details: list[str]

    def __str__(self) -> str:
        details_joined = "\n".join(self.description_details)
        return f"{self.title}\n{self.company}\n{details_joined}"