from pydantic import BaseModel


class JobDetails(BaseModel):
    title: str
    company: str
    description: str

    def __str__(self) -> str:
        return f"{self.title}\n{self.company}\n{self.description}"