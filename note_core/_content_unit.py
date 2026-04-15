from pydantic import BaseModel
from ._content_role import ContentRole

class ContentUnit(BaseModel):
    reasoning_content: str = ""
    content: str = ""
    role: ContentRole = ContentRole.SYSTEM