import json
import time
import httpx
import random
import asyncio
import aiofiles
from ._timer import Timer
from ._config import Config
from ._response import NoteResponse
from ._format_out import FormatOutput
from pydantic import ValidationError
from datetime import datetime
from loguru import logger
from pathlib import Path

class NoteCore:
    def __init__(self, config: Config):
        self._config = config
        self._client = httpx.AsyncClient()
        self._prompt: str = ""
    
    async def load_prompt(self):
        path = Path(self._config.prompt_file)
        if not path.exists():
            logger.error(f"Prompt file not found: {self._config.prompt_file}")
            raise FileNotFoundError(f"Prompt file not found: {self._config.prompt_file}")
        logger.info(f"Load prompt from {self._config.prompt_file}")
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            self._prompt = await f.read()
    
    async def get_user_id_list(self) -> list[str]:
        logger.info("Getting userid list...")
        response = await self._client.get(
            f"{self._config.server.protocol.value}://"
            f"{self._config.server.host}:{self._config.server.port}"
            "/userdata/context/userlist"
        )
        user_id_list = response.json()
        if not isinstance(user_id_list, list):
            logger.error("Invalid userid list")
            raise ValueError("Invalid userid list")
        logger.info(f"Got {len(user_id_list)} userids")
        return user_id_list
    
    async def send_request(self, reference_context_user_id: str | None = None):
        logger.info("Sending request to {host}:{port}...", host = self._config.server.host, port = self._config.server.port)
        start = time.monotonic_ns()
        
        for i in range(self._config.retry_times):
            try:
                if i > 0:
                    logger.info(f"Retrying ({i + 1}/{self._config.retry_times})...")
                response = await self._client.post(
                    (
                        f"{self._config.server.protocol.value}://"
                        f"{self._config.server.host}:{self._config.server.port}"
                        f"/chat/completion/{self._config.namespace}"
                    ),
                    json = {
                        "message": self._prompt,
                        "reference_context_id": reference_context_user_id,
                        "save_context": False,
                    },
                    timeout = self._config.server.timeout,
                )
                break
            except Exception as e:
                logger.error(f"Request failed: {e}")
                asyncio.sleep(self._config.retry_interval)
        end = time.monotonic_ns()
        logger.info(f"Request sent in {(end - start) / 1e9:.3f} seconds")

        if response.status_code == 200:
            try:
                return NoteResponse(
                    **response.json()
                )
            except json.JSONDecodeError:
                logger.error(f"Failed to get note response: {response.status_code}")
                raise
            except ValidationError as e:
                errors = e.errors()
                for error in errors:
                    logger.error(f"Validation error: {error['msg']}")
                    logger.error(f"Field: {'.'.join(error['loc'])}")
                    logger.error(f"CTX: {error['ctx']}")
                raise
        else:
            logger.error(f"Error sending request: {response.status_code}")
            return None
    
    async def save_note(self, response: NoteResponse, reference_context_user_id: str | None = None):
        now = datetime.now()
        path = (
            Path(self._config.output_dir) /
            now.strftime("%Y-%m-%d") /
            f"[{now.strftime('%Y-%m-%d-%H-%M-%S')}] "
            f"{response.id}{self._config.output_file_suffix}"
        )
        if not path.parent.exists():
            path.parent.mkdir(parents=True)
        fout = FormatOutput(
            output_format = self._config.output_format,
            path = path,
            time = now,
            reference_context_user_id = reference_context_user_id
        )
        await fout.output(response = response)
        
        logger.info(
            "Saved note to file: {file_path}",
            file_path = str(path)
        )
    
    async def close(self):
        await self._client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    
    async def timer_loop(self):
        async def create_note():
            user_id_list = await self.get_user_id_list()
            reference_context_user_id = random.choice(user_id_list)
            logger.info(f"Using reference context userid: {reference_context_user_id}")
            response = await self.send_request(reference_context_user_id)
            if response is None:
                logger.error("Request failed")
            else:
                await self.save_note(
                    response = response,
                    reference_context_user_id = reference_context_user_id
                )
        
        timer = Timer(create_note)
        await timer.start(run_once_first = True)