from pydantic import BaseModel, Field
from enum import Enum

class Agreement(Enum):
    HTTP = "http"
    HTTPS = "https"

class ServerConfig(BaseModel):
    host: str = '127.0.0.1'
    port: int = 8000
    protocol: Agreement = Agreement.HTTP
    timeout: float = 60.0

class Config(BaseModel):
    # 服务器配置
    server: ServerConfig = Field(default_factory = ServerConfig)
    namespace: str = "Note_Book"
    prompt_file: str = "./prompt/default.txt"
    output_dir: str = "./output"
    output_file_suffix: str = ".md"
    retry_times: int = 3
    retry_interval: float = 0.5