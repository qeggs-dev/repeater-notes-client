from pydantic import BaseModel, Field
from enum import StrEnum

class Agreement(StrEnum):
    HTTP = "http"
    HTTPS = "https"

class OutputFormat(StrEnum):
    TEXT = "text"
    JSON = "json"
    YAML = "yaml"

class ServerConfig(BaseModel):
    host: str = '127.0.0.1'
    port: int = 8000
    protocol: Agreement = Agreement.HTTP
    timeout: float = 60.0

class UserInfoConfig(BaseModel):
    username: str | None = None
    nickname: str | None = None
    age: int | None = None
    gender: str | None = None

class Config(BaseModel):
    # 服务器配置
    server: ServerConfig = Field(default_factory = ServerConfig)
    namespace: str = "Note_Book"
    prompt_file: str = "./prompt/default.txt"
    output_dir: str = "./output"
    output_file_suffix: str = ".md"
    user_info: UserInfoConfig = Field(default_factory = UserInfoConfig)
    output_format: OutputFormat = OutputFormat.TEXT
    retry_times: int = 3
    retry_interval: float = 0.5