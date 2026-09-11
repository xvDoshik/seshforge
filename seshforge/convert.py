from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from telethon.crypto import AuthKey
from telethon.sessions import MemorySession, SQLiteSession, StringSession

DC_IPV4 = {
    1: "149.154.175.53",
    2: "149.154.167.51",
    3: "149.154.175.100",
    4: "149.154.167.91",
    5: "91.108.56.130",
}
DC_IPV4_TEST = {
    1: "149.154.175.10",
    2: "149.154.167.40",
    3: "149.154.175.117",
}
DEFAULT_PORT = 443

SessionKind = Literal["telethon", "pyrogram", "unknown"]


@dataclass(frozen=True)
class AuthParts:
    dc_id: int
    auth_key: bytes
    server_address: str | None = None
    port: int = DEFAULT_PORT
    api_id: int | None = None
    test_mode: bool = False
    user_id: int | None = None
    is_bot: bool = False


def detect_string_kind(value: str) -> SessionKind:
    raw = value.strip()
    if not raw:
        return "unknown"
    try:
        from seshforge.pyro_session import looks_like_pyrogram_string

        if looks_like_pyrogram_string(raw):
            return "pyrogram"
    except Exception:
        pass
    if raw[0] == "1" and len(raw) > 50 and "/" not in raw and "\\" not in raw:
        try:
            StringSession(raw)
            return "telethon"
        except Exception:
            pass
    return "unknown"


def dc_address(dc_id: int, *, test_mode: bool = False) -> tuple[str, int]:
    table = DC_IPV4_TEST if test_mode else DC_IPV4
    if dc_id not in table:
        raise ValueError(f"unknown dc_id={dc_id}")
    return table[dc_id], DEFAULT_PORT


def memory_from_parts(
    dc_id: int,
    address: str,
    port: int,
    auth_key: bytes,
) -> StringSession:
    ss = StringSession()
    ss.set_dc(dc_id, address, port)
    ss.auth_key = AuthKey(auth_key)
    return ss


def session_to_string(session: Any) -> str:
    if isinstance(session, StringSession):
        return session.save() or ""
    if not getattr(session, "auth_key", None):
        raise ValueError("session has no auth_key")
    out = StringSession()
    out.set_dc(session.dc_id, session.server_address, session.port)
    out.auth_key = session.auth_key
    return out.save() or ""


def string_to_session(session_string: str) -> StringSession:
    kind = detect_string_kind(session_string)
    if kind == "telethon":
        return StringSession(session_string.strip())
    if kind == "pyrogram":
        from seshforge.pyro_session import pyrogram_string_to_telethon_string

        return StringSession(pyrogram_string_to_telethon_string(session_string))
    raise ValueError("unrecognized session string format")


def _resolve_telethon_stem(path: str | Path) -> str:
    path = Path(path).expanduser().resolve()
    if path.suffix == ".session":
        if not path.exists():
            raise FileNotFoundError(path)
        return str(path.with_suffix(""))
    candidate = Path(str(path) + ".session")
    if candidate.exists():
        return str(path)
    if path.exists() and path.is_file():
        return str(path.with_suffix("")) if path.suffix == ".session" else str(path)
    raise FileNotFoundError(path)


def session_file_to_string(path: str | Path) -> str:
    stem = _resolve_telethon_stem(path)
    sqlite = SQLiteSession(stem)
    try:
        if not sqlite.auth_key:
            raise ValueError(f"no auth_key in session file: {path}")
        return session_to_string(sqlite)
    finally:
        close = getattr(sqlite, "close", None)
        if callable(close):
            close()


def string_to_session_file(session_string: str, path: str | Path) -> Path:
    path = Path(path).expanduser().resolve()
    if path.suffix == ".session":
        stem = path.with_suffix("")
        out = path
    else:
        stem = path
        out = Path(str(path) + ".session")
    out.parent.mkdir(parents=True, exist_ok=True)
    src = string_to_session(session_string)
    if out.exists():
        out.unlink()
    sqlite = SQLiteSession(str(stem))
    try:
        sqlite.set_dc(src.dc_id, src.server_address, src.port)
        sqlite.auth_key = src.auth_key
        sqlite.save()
    finally:
        sqlite.close()
    return out


def list_telethon_sessions() -> list[str]:
    return list(SQLiteSession.list_sessions())


def auth_parts_from_telethon_string(session_string: str) -> AuthParts:
    ss = StringSession(session_string.strip())
    if not ss.auth_key:
        raise ValueError("telethon string has no auth_key")
    return AuthParts(
        dc_id=ss.dc_id,
        auth_key=ss.auth_key.key,
        server_address=ss.server_address,
        port=ss.port or DEFAULT_PORT,
    )


def telethon_string_from_parts(parts: AuthParts) -> str:
    address = parts.server_address
    port = parts.port
    if not address:
        address, port = dc_address(parts.dc_id, test_mode=parts.test_mode)
    return session_to_string(memory_from_parts(parts.dc_id, address, port, parts.auth_key))


async def tdata_to_string(
    tdata_path: str | Path,
    *,
    account_index: int = 0,
    use_current: bool = True,
    passcode: str | None = None,
    key_file: str | None = None,
    api: Any = None,
    password: str | None = None,
) -> str:
    from seshforge.desktop import tdata_to_telethon_string

    return await tdata_to_telethon_string(
        tdata_path,
        account_index=account_index,
        use_current=use_current,
        passcode=passcode,
        key_file=key_file,
        api=api,
        password=password,
    )


async def string_to_tdata(
    session_string: str,
    out_path: str | Path,
    *,
    api_id: int,
    api_hash: str,
    use_current: bool = True,
    password: str | None = None,
    api: Any = None,
) -> Path:
    from seshforge.desktop import telethon_to_tdata

    return await telethon_to_tdata(
        session_string,
        out_path,
        api_id=api_id,
        api_hash=api_hash,
        use_current=use_current,
        password=password,
        api=api,
    )


__all__ = [
    "AuthParts",
    "DC_IPV4",
    "DEFAULT_PORT",
    "MemorySession",
    "SQLiteSession",
    "StringSession",
    "auth_parts_from_telethon_string",
    "dc_address",
    "detect_string_kind",
    "list_telethon_sessions",
    "memory_from_parts",
    "session_file_to_string",
    "session_to_string",
    "string_to_session",
    "string_to_session_file",
    "string_to_tdata",
    "tdata_to_string",
    "telethon_string_from_parts",
]
