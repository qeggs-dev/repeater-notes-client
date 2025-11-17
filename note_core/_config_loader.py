from ._config import Config
from loguru import logger
from pathlib import Path
import aiofiles
import orjson
import yaml
import os

class ConfigLoader:
    """
    ConfigLoader is a class that loads the configuration from the config file.
    """

    def __init__(self, config_file: str | os.PathLike):
        self._config_file: Path = Path(config_file)
        self._config: Config = Config()
    
    @property
    def config(self):
        return self._config
    
    @config.setter
    def config(self, config: Config):
        if isinstance(config, Config):
            self._config = config
        else:
            raise TypeError("Config must be an instance of Config")

    async def load(self, fail_writes_default: bool = True):
        """
        Loads the configuration from the config file.
        """
        if self._config_file.suffix == '.json':
            try:
                self._config = await self._load_json()
            except (FileNotFoundError, orjson.JSONDecodeError):
                if fail_writes_default:
                    logger.warning("Loading config failed. Saving default config.")
                    await self._save_json()
                else:
                    raise
        elif self._config_file.suffix == '.yaml':
            try:
                self._config = await self._load_yaml()
            except (FileNotFoundError, yaml.YAMLError):
                if fail_writes_default:
                    logger.warning("Loading config failed. Saving default config.")
                    await self._save_yaml()
                else:
                    raise
        else:
            raise ValueError('Unsupported file format')
        
        return self._config
    
    async def _load_json(self):
        """
        Loads the configuration from the config file in JSON format.
        """
        logger.debug(f"Loading config from {self._config_file}")
        async with aiofiles.open(self._config_file, 'rb') as f:
            data = await f.read()
            return Config(**orjson.loads(data))
    
    async def _load_yaml(self):
        """
        Loads the configuration from the config file in YAML format.
        """
        logger.debug(f"Loading config from {self._config_file}")
        async with aiofiles.open(self._config_file, 'r') as f:
            data = await f.read()
            return Config(**yaml.safe_load(data))

    async def save(self):
        """
        Saves the configuration to the config file.
        """
        if self._config_file.suffix == '.json':
            await self._save_json()
        elif self._config_file.suffix == '.yaml':
            await self._save_yaml()
        else:
            raise ValueError('Unsupported file format')

    async def _save_json(self):
        """
        Saves the configuration to the config file in JSON format.
        """
        logger.debug(f"Saving config to {self._config_file}")
        async with aiofiles.open(self._config_file, 'wb') as f:
            await f.write(orjson.dumps(self._config.model_dump()))

    async def _save_yaml(self):
        """
        Saves the configuration to the config file in YAML format.
        """
        logger.debug(f"Saving config to {self._config_file}")
        async with aiofiles.open(self._config_file, 'w') as f:
            await f.write(yaml.safe_dump(self._config.model_dump()))