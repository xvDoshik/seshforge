from __future__ import annotations

from typing import Any

__all__ = [
    "API",
    "APIData",
    "CreateNewSession",
    "LoginFlag",
    "UseCurrentSession",
]


def __getattr__(name: str) -> Any:
    if name in __all__:
        from opentele.api import (
            API,
            APIData,
            CreateNewSession,
            LoginFlag,
            UseCurrentSession,
        )

        mapping = {
            "API": API,
            "APIData": APIData,
            "CreateNewSession": CreateNewSession,
            "LoginFlag": LoginFlag,
            "UseCurrentSession": UseCurrentSession,
        }
        return mapping[name]
    raise AttributeError(name)
