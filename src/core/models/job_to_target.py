from pydantic import BaseModel


class JobDetails(BaseModel):
    url: str
    title: str
    company: str
    description_details: list[str]

    def __str__(self) -> str:
        return f"{self.title}\n{self.company}\n{"\n".join(self.description_details)}"