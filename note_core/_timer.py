import random
import asyncio
import datetime
from typing import Callable, Any, Awaitable
from loguru import logger

class Timer:
    def __init__(self, callback: Callable[..., Awaitable[Any]], *args, **kwargs):
        self._callback = callback
        self._args = args
        self._kwargs = kwargs
    
    @staticmethod
    def get_next_random_time():
        """计算下一个随机时间点"""
        now = datetime.datetime.now()
        
        # 明天0点
        tomorrow_0am = (now + datetime.timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        
        # 在24小时内随机选择一个时间点
        random_seconds = random.randint(0, 24 * 3600 - 1)
        target_time = tomorrow_0am + datetime.timedelta(seconds=random_seconds)
        
        return target_time
    
    async def _start_run_once_first(self):
        while True:
            await self._callback(*self._args, **self._kwargs)
            
            next_time = self.get_next_random_time()
            sleep_duration = next_time - datetime.datetime.now()
            sleep_seconds = sleep_duration.total_seconds()

            logger.info(
                "Next run at {next_time}",
                next_time = next_time.strftime("%Y-%m-%d %H:%M:%S"),
            )

            await asyncio.sleep(sleep_seconds)
    
    async def _start(self, run_once_first: bool = False):
        while True:
            next_time = self.get_next_random_time()
            sleep_duration = next_time - datetime.datetime.now()
            sleep_seconds = sleep_duration.total_seconds()

            logger.info(
                "Next run at {next_time}",
                next_time = next_time.strftime("%Y-%m-%d %H:%M:%S"),
            )

            await asyncio.sleep(sleep_seconds)

            await self._callback(*self._args, **self._kwargs)
    
    async def start(self, run_once_first: bool = False):
        if run_once_first:
            await self._start_run_once_first()
        else:
            await self._start()