import json
import time
import httpx
import asyncio
import aiofiles
from ._timer import Timer
from ._config import Config
from ._response import NoteResponse
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
    
    async def send_request(self):
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
                        "reference_context_id": "[Random]",
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
    
    async def save_note(self, response: NoteResponse):
        now = datetime.now()
        path = (
            Path(self._config.output_dir) /
            f"[{now.strftime('%Y-%m-%d-%H-%M-%S')}] "
            f"{response.id}{self._config.output_file_suffix}"
        )
        if not path.parent.exists():
            path.parent.mkdir(parents=True)
        async with aiofiles.open(path, "w", encoding="utf-8") as f:
            await f.write("# Repeater Note\n")
            await f.write(f"- Note ID: {response.id}\n")
            await f.write(f"- Time: {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
            await f.write(f"- Model ID: {response.model_id}\n")
            if response.reasoning_content:
                await f.write(f"\n## CoT: \n{response.reasoning_content}\n")
            if response.content:
                await f.write(f"\n## Answer: \n{response.content}")
        
        logger.info(
            "Saved note to file: {file_path}",
            file_path = str(path.absolute())
        )
    
    async def close(self):
        await self._client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    
    async def timer_loop(self):
        async def create_note():
            response = await self.send_request()
            if response is None:
                logger.error("Request failed")
            else:
                await self.save_note(response = response)
        
        timer = Timer(create_note)
        await timer.start(run_once_first = True)