from pydantic import BaseModel, Field
from ._content_unit import ContentUnit
from ._content_role import ContentRole

class ContextObject(BaseModel):
    context_list: list[ContentUnit] = Field(default_factory=list)

class NoteResponse(BaseModel):
    id: str = ""
    status: int = 200
    context: ContextObject = Field(default_factory=ContextObject)
    model_id: str = ""
    model_name: str = ""
    model_type: str = ""
    create_time: int = 0
    finish_reason_cause: str = ""

    @property
    def reasoning_content(self) -> str:
        buffer: list[str] = []
        for content in self.context.context_list:
            if content.role == ContentRole.USER:
                buffer.append(content.content)
        return "\n\n".join(buffer)
    
    @property
    def content(self):
        buffer: list[str] = []
        for content in self.context.context_list:
            if content.role == ContentRole.ASSISTANT:
                buffer.append(content.content)
        return "\n\n".join(buffer)
