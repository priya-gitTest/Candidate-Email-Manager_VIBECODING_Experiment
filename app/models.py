from pydantic import BaseModel, EmailStr

class Candidate(BaseModel):
    name: str
    email: EmailStr

class CandidateInDB(Candidate):
    id: int
    stage: int