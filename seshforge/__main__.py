#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")
load_dotenv()

API_ID = int(os.getenv("API_ID", "2040"))
API_HASH = os.getenv("API_HASH", "b18441a1ff607e10a989891a5462e627")


def _print_result(session: str, me) -> None:
    print()
    print("ok")
    print(f"account: {me.first_name} (@{me.username or '-'}) id={me.id}")
    print()
    print("SESSION_STRING=")
    print(session)


async def _load_client(args) -> "Client":
    from seshforge import Client

    if args.tdata:
        return await Client.from_tdata(
            args.tdata,
            API_ID,
            API_HASH,
            account_index=args.account,
            use_current=not args.qr,
        )
    if args.session:
        return await Client.from_session_file(args.session, API_ID, API_HASH)
    if args.string:
        return await Client.from_string(args.string, API_ID, API_HASH)
    if args.pyrogram_session:
        return await Client.from_pyrogram_file(args.pyrogram_session, API_ID, API_HASH)
    if args.pyrogram_string:
        return await Client.from_pyrogram_string(args.pyrogram_string, API_ID, API_HASH)
    raise ValueError("no input source")


async def async_main() -> None:
    args = build_parser().parse_args()
    client = await _load_client(args)
    try:
        me = await client.get_me()
        if me is None:
            raise SystemExit("not authorized")
        session = client.session_string
        _print_result(session, me)

        if args.to_tdata:
            out = await client.to_tdata(args.to_tdata, use_current=not args.qr)
            print(f"wrote tdata: {out}")
        if args.to_session:
            out = client.to_session_file(args.to_session)
            print(f"wrote telethon session: {out}")
        if args.to_pyrogram_session:
            out = await client.to_pyrogram_file(args.to_pyrogram_session)
            print(f"wrote pyrogram session: {out}")
        if args.to_pyrogram_string:
            pyro = await client.export_pyrogram_string()
            print()
            print("PYROGRAM_STRING=")
            print(pyro)
    finally:
        await client.disconnect()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="seshforge",
        description="Forge / convert Telethon + Pyrogram + Desktop sessions (lock-free Telethon runtime)",
    )
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--tdata", metavar="PATH", help="Telegram Desktop tdata directory")
    g.add_argument("--session", metavar="PATH", help="Telethon .session file")
    g.add_argument("--string", metavar="STR", help="Telethon StringSession")
    g.add_argument("--pyrogram-session", metavar="PATH", help="Pyrogram .session SQLite")
    g.add_argument("--pyrogram-string", metavar="STR", help="Pyrogram session string")
    p.add_argument("--account", type=int, default=0, help="tdata account index (default 0)")
    p.add_argument(
        "--qr",
        action="store_true",
        help="CreateNewSession / QR instead of UseCurrentSession",
    )
    p.add_argument("--to-tdata", metavar="OUT", help="export Desktop tdata directory")
    p.add_argument("--to-session", metavar="OUT", help="export Telethon .session")
    p.add_argument("--to-pyrogram-session", metavar="OUT", help="export Pyrogram .session")
    p.add_argument(
        "--to-pyrogram-string",
        action="store_true",
        help="also print Pyrogram session string",
    )
    return p


def main() -> None:
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\ncanceled", file=sys.stderr)
        raise SystemExit(130) from None


if __name__ == "__main__":
    main()
