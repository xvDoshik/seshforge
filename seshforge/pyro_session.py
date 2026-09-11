from __future__ import annotations

import base64
import sqlite3
import struct
import time
from pathlib import Path

from seshforge.convert import (
    AuthParts,
    auth_parts_from_telethon_string,
    dc_address,
    session_to_string,
    telethon_string_from_parts,
)

SESSION_STRING_FORMAT = ">BI?256sQ?"
OLD_SESSION_STRING_FORMAT = ">B?256sI?"
OLD_SESSION_STRING_FORMAT_64 = ">B?256sQ?"
SESSION_STRING_SIZE = 351
SESSION_STRING_SIZE_64 = 356

SCHEMA = """
CREATE TABLE sessions
(
    dc_id     INTEGER PRIMARY KEY,
    api_id    INTEGER,
    test_mode INTEGER,
    auth_key  BLOB,
    date      INTEGER NOT NULL,
    user_id   INTEGER,
    is_bot    INTEGER
);
CREATE TABLE peers
(
    id             INTEGER PRIMARY KEY,
    access_hash    INTEGER,
    type           INTEGER NOT NULL,
    username       TEXT,
    phone_number   TEXT,
    last_update_on INTEGER NOT NULL DEFAULT (CAST(STRFTIME('%s', 'now') AS INTEGER))
);
CREATE TABLE version (number INTEGER PRIMARY KEY);
"""


def looks_like_pyrogram_string(value: str) -> bool:
    raw = value.strip()
    padded = raw + "=" * (-len(raw) % 4)
    try:
        data = base64.urlsafe_b64decode(padded)
    except Exception:
        return False
    if len(raw) in (SESSION_STRING_SIZE, SESSION_STRING_SIZE_64):
        return True
    if len(data) == struct.calcsize(SESSION_STRING_FORMAT):
        return True
    if len(data) in (
        struct.calcsize(OLD_SESSION_STRING_FORMAT),
        struct.calcsize(OLD_SESSION_STRING_FORMAT_64),
    ):
        return True
    return False


def unpack_pyrogram_string(session_string: str) -> AuthParts:
    raw = session_string.strip()
    data = base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4))
    if len(raw) in (SESSION_STRING_SIZE, SESSION_STRING_SIZE_64) or len(data) in (
        struct.calcsize(OLD_SESSION_STRING_FORMAT),
        struct.calcsize(OLD_SESSION_STRING_FORMAT_64),
    ):
        if len(data) == struct.calcsize(OLD_SESSION_STRING_FORMAT):
            dc_id, test_mode, auth_key, user_id, is_bot = struct.unpack(
                OLD_SESSION_STRING_FORMAT, data
            )
            api_id = None
        else:
            dc_id, test_mode, auth_key, user_id, is_bot = struct.unpack(
                OLD_SESSION_STRING_FORMAT_64, data
            )
            api_id = None
    else:
        dc_id, api_id, test_mode, auth_key, user_id, is_bot = struct.unpack(
            SESSION_STRING_FORMAT, data
        )
    address, port = dc_address(int(dc_id), test_mode=bool(test_mode))
    return AuthParts(
        dc_id=int(dc_id),
        auth_key=auth_key,
        server_address=address,
        port=port,
        api_id=int(api_id) if api_id is not None else None,
        test_mode=bool(test_mode),
        user_id=int(user_id) if user_id else None,
        is_bot=bool(is_bot),
    )


def pack_pyrogram_string(parts: AuthParts, *, api_id: int | None = None) -> str:
    resolved_api = api_id if api_id is not None else parts.api_id
    if resolved_api is None:
        raise ValueError("api_id required to pack pyrogram session string")
    if parts.user_id is None:
        raise ValueError("user_id required to pack pyrogram session string")
    packed = struct.pack(
        SESSION_STRING_FORMAT,
        parts.dc_id,
        int(resolved_api),
        bool(parts.test_mode),
        parts.auth_key,
        int(parts.user_id),
        bool(parts.is_bot),
    )
    return base64.urlsafe_b64encode(packed).decode().rstrip("=")


def pyrogram_string_to_telethon_string(session_string: str) -> str:
    return telethon_string_from_parts(unpack_pyrogram_string(session_string))


def telethon_string_to_pyrogram_string(
    session_string: str,
    *,
    api_id: int,
    user_id: int,
    is_bot: bool = False,
    test_mode: bool = False,
) -> str:
    base = auth_parts_from_telethon_string(session_string)
    parts = AuthParts(
        dc_id=base.dc_id,
        auth_key=base.auth_key,
        server_address=base.server_address,
        port=base.port,
        api_id=api_id,
        test_mode=test_mode,
        user_id=user_id,
        is_bot=is_bot,
    )
    return pack_pyrogram_string(parts, api_id=api_id)


def _resolve_pyrogram_db(path: str | Path) -> Path:
    path = Path(path).expanduser().resolve()
    if path.suffix == ".session" and path.exists():
        return path
    candidate = Path(str(path) + ".session")
    if candidate.exists():
        return candidate
    if path.exists() and path.is_file():
        return path
    raise FileNotFoundError(path)


def pyrogram_file_to_parts(path: str | Path) -> AuthParts:
    db = _resolve_pyrogram_db(path)
    con = sqlite3.connect(str(db))
    try:
        row = con.execute(
            "SELECT dc_id, api_id, test_mode, auth_key, user_id, is_bot FROM sessions LIMIT 1"
        ).fetchone()
        if not row:
            raise ValueError(f"empty pyrogram session db: {db}")
        dc_id, api_id, test_mode, auth_key, user_id, is_bot = row
        if not auth_key:
            raise ValueError(f"no auth_key in pyrogram session: {db}")
        address, port = dc_address(int(dc_id), test_mode=bool(test_mode))
        return AuthParts(
            dc_id=int(dc_id),
            auth_key=bytes(auth_key),
            server_address=address,
            port=port,
            api_id=int(api_id) if api_id is not None else None,
            test_mode=bool(test_mode),
            user_id=int(user_id) if user_id else None,
            is_bot=bool(is_bot),
        )
    finally:
        con.close()


def pyrogram_file_to_string(path: str | Path) -> str:
    return telethon_string_from_parts(pyrogram_file_to_parts(path))


def pyrogram_file_to_pyrogram_string(path: str | Path) -> str:
    parts = pyrogram_file_to_parts(path)
    return pack_pyrogram_string(parts)


def string_to_pyrogram_file(
    session_string: str,
    path: str | Path,
    *,
    api_id: int | None = None,
    user_id: int | None = None,
    is_bot: bool = False,
    test_mode: bool = False,
    name: str | None = None,
) -> Path:
    from seshforge.convert import detect_string_kind

    kind = detect_string_kind(session_string)
    if kind == "pyrogram":
        parts = unpack_pyrogram_string(session_string)
    elif kind == "telethon":
        if user_id is None:
            raise ValueError("user_id required when writing pyrogram file from telethon string")
        if api_id is None:
            raise ValueError("api_id required when writing pyrogram file from telethon string")
        base = auth_parts_from_telethon_string(session_string)
        parts = AuthParts(
            dc_id=base.dc_id,
            auth_key=base.auth_key,
            server_address=base.server_address,
            port=base.port,
            api_id=api_id,
            test_mode=test_mode,
            user_id=user_id,
            is_bot=is_bot,
        )
    else:
        raise ValueError("unrecognized session string")

    path = Path(path).expanduser().resolve()
    if path.suffix == ".session":
        out = path
    elif name:
        out = path / f"{name}.session"
    else:
        out = Path(str(path) + ".session") if path.suffix != ".session" else path
        if path.is_dir():
            out = path / "seshforge.session"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    con = sqlite3.connect(str(out))
    try:
        con.executescript(SCHEMA)
        con.execute("INSERT INTO version VALUES (3)")
        con.execute(
            "INSERT INTO sessions VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                parts.dc_id,
                parts.api_id,
                int(parts.test_mode),
                parts.auth_key,
                int(time.time()),
                parts.user_id,
                int(parts.is_bot),
            ),
        )
        con.commit()
    finally:
        con.close()
    return out


async def open_pyrogram(
    api_id: int,
    api_hash: str,
    *,
    session_string: str | None = None,
    session_file: str | Path | None = None,
    tdata: str | Path | None = None,
    telethon_string: str | None = None,
    account_index: int = 0,
    user_id: int | None = None,
    is_bot: bool = False,
    test_mode: bool = False,
    name: str = "seshforge",
    workdir: str | Path = ".",
    **kwargs,
):
    from pyrogram import Client

    from seshforge.convert import detect_string_kind, tdata_to_string

    sources = [session_string, session_file, tdata, telethon_string]
    if sum(x is not None for x in sources) != 1:
        raise ValueError(
            "pass exactly one of: session_string, session_file, tdata, telethon_string"
        )

    pyro_string: str | None = None
    if session_string is not None:
        kind = detect_string_kind(session_string)
        if kind == "pyrogram":
            pyro_string = session_string.strip()
        elif kind == "telethon":
            if user_id is None:
                raise ValueError("user_id required when opening pyrogram from telethon string")
            pyro_string = telethon_string_to_pyrogram_string(
                session_string,
                api_id=api_id,
                user_id=user_id,
                is_bot=is_bot,
                test_mode=test_mode,
            )
        else:
            raise ValueError("unrecognized session string")
    elif session_file is not None:
        pyro_string = pyrogram_file_to_pyrogram_string(session_file)
    elif tdata is not None:
        tl = await tdata_to_string(tdata, account_index=account_index)
        if user_id is None:
            raise ValueError("user_id required when opening pyrogram from tdata")
        pyro_string = telethon_string_to_pyrogram_string(
            tl,
            api_id=api_id,
            user_id=user_id,
            is_bot=is_bot,
            test_mode=test_mode,
        )
    elif telethon_string is not None:
        if user_id is None:
            raise ValueError("user_id required when opening pyrogram from telethon_string")
        pyro_string = telethon_string_to_pyrogram_string(
            telethon_string,
            api_id=api_id,
            user_id=user_id,
            is_bot=is_bot,
            test_mode=test_mode,
        )

    return Client(
        name=name,
        api_id=api_id,
        api_hash=api_hash,
        session_string=pyro_string,
        workdir=str(workdir),
        in_memory=True,
        **kwargs,
    )


__all__ = [
    "looks_like_pyrogram_string",
    "open_pyrogram",
    "pack_pyrogram_string",
    "pyrogram_file_to_parts",
    "pyrogram_file_to_pyrogram_string",
    "pyrogram_file_to_string",
    "pyrogram_string_to_telethon_string",
    "string_to_pyrogram_file",
    "telethon_string_to_pyrogram_string",
    "unpack_pyrogram_string",
]
