import os
import sys
import asyncio
from note_core import NoteCore, ConfigLoader
from loguru import logger
from pathlib import Path
from itertools import chain
from typing import Coroutine, Generator

logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> - <level>{message}</level>",
    enqueue = True,
)
logger.add(
    "logs/{time:YYYY-MM-DD_HH-mm-ss}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    enqueue = True,
    rotation="00:00",
    retention="7 days",
    compression="zip",
    delay=True,
)

def find_config_file(base_path: str | os.PathLike) -> Generator[Path, None, None]:
    if not Path(base_path).is_dir():
        raise NotADirectoryError(f"{base_path} is not a directory")
    combined = chain(
        Path(base_path).rglob('*.yaml'),
        Path(base_path).rglob('*.yml'),
        Path(base_path).rglob('*.json')
    )
    for file in combined:
        if file.is_file() and not file.name.startswith("#"):
            yield file

async def run_timer_loop(path: Path):
    logger.info(f"Worker {path.stem} is running")
    loader = ConfigLoader(path)
    config = await loader.load()
    async with NoteCore(config) as core:
        await core.load_prompt()
        await core.timer_loop()

async def main():
    try:
        config_file: Generator[Path, None, None] = find_config_file("./config")
        pool: set[Coroutine] = set()
        for file in config_file:
            pool.add(
                asyncio.create_task(
                    run_timer_loop(file)
                )
            )
        
        await asyncio.gather(*pool)
    except Exception as e:
        logger.exception("An error occurred: {error}", error = e)
        

if __name__ == "__main__":
    asyncio.run(main())