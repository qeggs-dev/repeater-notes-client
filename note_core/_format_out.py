import aiofiles
import orjson
import yaml
from datetime import datetime
from ._response import NoteResponse
from ._config import OutputFormat
from pathlib import Path

class FormatOutput:
    def __init__(
            self,
            output_format: OutputFormat,
            path: Path,
            time: datetime | None = None,
            reference_context_user_id: str | None = None,
        ):
        self._output_format = output_format
        self._path = path
        self._time = time or datetime.now()
        self._reference_context_user_id = reference_context_user_id
    
    async def output(self, response: NoteResponse):
        if self._output_format == OutputFormat.TEXT:
            await self._format_text(response)
        elif self._output_format == OutputFormat.JSON:
            await self._format_json(response)
        elif self._output_format == OutputFormat.YAML:
            await self._format_yaml(response)
        else:
            raise ValueError("Invalid output format")
    
    async def _format_text(self, response: NoteResponse):
        async with aiofiles.open(self._path, "w", encoding="utf-8") as f:
            await f.write("# Repeater Note\n")
            await f.write(f"- Note ID: {response.id}\n")
            await f.write(f"- Time: {self._time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            await f.write(f"- Model ID: {response.model_id}\n")
            await f.write(f"- Reference Context User ID: {self._reference_context_user_id}\n")
            if response.reasoning_content:
                await f.write(f"\n## CoT: \n{response.reasoning_content}\n")
            if response.content:
                await f.write(f"\n## Answer: \n{response.content}")
    
    def _output_dict(self, response: NoteResponse):
        return {
            "Note ID": response.id,
            "Time": self._time.strftime('%Y-%m-%d %H:%M:%S'),
            "Model ID": response.model_id,
            "Reference Context User ID": self._reference_context_user_id,
            "CoT": response.reasoning_content,
            "Answer": response.content
        }
    
    async def _format_json(self, response: NoteResponse):
        async with aiofiles.open(self._path, 'wb') as f:
            await f.write(
                orjson.dumps(
                    self._output_dict(response)
                )
            )
    
    async def _format_yaml(self, response: NoteResponse):
        async with aiofiles.open(self._path, 'w', encoding='utf-8') as f:
            await f.write(
                yaml.safe_dump(
                    self._output_dict(response)
                )
            )