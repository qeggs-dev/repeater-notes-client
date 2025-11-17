from pydantic import BaseModel

class NoteResponse(BaseModel):
    id: str = ""
    status: int = 200
    reasoning_content: str = ""
    content: str = ""
    model_id: str = ""
    model_name: str = ""
    model_type: str = ""
    create_time: int = 0
    finish_reason_cause: str = ""