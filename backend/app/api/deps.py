"""Dependency Injection for API routes"""

from typing import Annotated

from fastapi import Depends

from app.config import Settings, get_settings
from app.services.storage.base import BaseStorageClient
from app.services.storage.local_client import LocalStorageClient
from app.services.llm.base import BaseLLMClient
from app.services.llm.nvidia_client import NvidiaClient


def get_storage_client(
    settings: Annotated[Settings, Depends(get_settings)]
) -> BaseStorageClient:
    """Get Storage client"""
    return LocalStorageClient(
        storage_path=settings.STORAGE_PATH,
        base_url=settings.BASE_URL,
    )


def get_llm_client(
    settings: Annotated[Settings, Depends(get_settings)]
) -> BaseLLMClient:
    """Get LLM client based on configuration"""
    if settings.LLM_PROVIDER == "nvidia":
        return NvidiaClient(
            api_key=settings.NVIDIA_API_KEY,
            model=settings.LLM_MODEL,
            vision_model=settings.LLM_VISION_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
        )
    else:
        raise ValueError(f"Unknown LLM provider: {settings.LLM_PROVIDER}")


# Type aliases for dependency injection
StorageClientDep = Annotated[BaseStorageClient, Depends(get_storage_client)]
LLMClientDep = Annotated[BaseLLMClient, Depends(get_llm_client)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
