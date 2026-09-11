from __future__ import annotations

from typing import Any

from seshforge.client import Client
from seshforge.convert import (
    AuthParts,
    MemorySession,
    SQLiteSession,
    StringSession,
    auth_parts_from_telethon_string,
    dc_address,
    detect_string_kind,
    list_telethon_sessions,
    memory_from_parts,
    session_file_to_string,
    session_to_string,
    string_to_session,
    string_to_session_file,
    string_to_tdata,
    tdata_to_string,
    telethon_string_from_parts,
)
from seshforge.pyro_session import (
    looks_like_pyrogram_string,
    open_pyrogram,
    pack_pyrogram_string,
    pyrogram_file_to_parts,
    pyrogram_file_to_pyrogram_string,
    pyrogram_file_to_string,
    pyrogram_string_to_telethon_string,
    string_to_pyrogram_file,
    telethon_string_to_pyrogram_string,
    unpack_pyrogram_string,
)

__version__ = "0.2.0"

__all__ = [
    "API",
    "APIData",
    "AuthParts",
    "Client",
    "CreateNewSession",
    "LoginFlag",
    "MemorySession",
    "SQLiteSession",
    "StringSession",
    "UseCurrentSession",
    "accounts_count",
    "auth_parts_from_telethon_string",
    "dc_address",
    "detect_string_kind",
    "list_accounts",
    "list_telethon_sessions",
    "load_tdata",
    "looks_like_pyrogram_string",
    "main_account",
    "memory_from_parts",
    "open_pyrogram",
    "pack_pyrogram_string",
    "pyrogram_file_to_parts",
    "pyrogram_file_to_pyrogram_string",
    "pyrogram_file_to_string",
    "pyrogram_string_to_telethon_string",
    "save_tdata",
    "session_file_to_string",
    "session_to_string",
    "string_to_pyrogram_file",
    "string_to_session",
    "string_to_session_file",
    "string_to_tdata",
    "tdata_to_string",
    "tdata_to_telethon_string",
    "telethon_string_from_parts",
    "telethon_string_to_pyrogram_string",
    "telethon_to_tdata",
    "unpack_pyrogram_string",
    "__version__",
]

_LAZY = frozenset(
    {
        "API",
        "APIData",
        "CreateNewSession",
        "LoginFlag",
        "UseCurrentSession",
        "accounts_count",
        "list_accounts",
        "load_tdata",
        "main_account",
        "save_tdata",
        "tdata_to_telethon_string",
        "telethon_to_tdata",
    }
)


def __getattr__(name: str) -> Any:
    if name in {"API", "APIData", "CreateNewSession", "LoginFlag", "UseCurrentSession"}:
        from seshforge import api as api_mod

        return getattr(api_mod, name)
    if name in _LAZY:
        from seshforge import desktop as desktop_mod

        return getattr(desktop_mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
