from pydantic import BaseModel, SecretStr
import yaml
from dotenv import load_dotenv
import os
from loguru import logger as log

class ServerConfig(BaseModel):
    port: int


class DatabaseConfig(BaseModel):
    username: str
    password: str
    host: str
    port: int
    database: str


class AppConfig(BaseModel):
    server: ServerConfig
    database: DatabaseConfig


def load_config(file_path: str) -> AppConfig:
    with open(file_path, 'r') as file:
        config_data = yaml.safe_load(file)
        return AppConfig(**config_data)


class Config:
    def __init__(self):
        load_dotenv()
        mode = os.getenv('run_mode')
        if mode is None:
            mode = "dev"
        log.info(f"Run mode = {mode}")
        path = f"resources/{mode}.yml"
        self.app = load_config(path)
        self.database = self.app.database
        self.server = self.app.server
        log.info(f"Config loaded from file {path}")
