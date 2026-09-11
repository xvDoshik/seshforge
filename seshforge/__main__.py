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

API_ID = int(os.getenv("API_ID", "2040"))
API_HASH = os.getenv("API_HASH", "b18441a1ff607e10a989891a5462e627")


def _print_result(session: str, me) -> None:
    print()
    print("ok")
    print(f"account: {me.first_name} (@{me.username or '-'}) id={me.id}")
    print()
    print("SESSION_STRING=")
    print(session)


async def run_tdata(path: str, account_index: int) -> None:
    from seshforge import Client

    client = await Client.from_tdata(path, API_ID, API_HASH, account_index=account_index)
    me = await client.get_me()
    _print_result(client.session_string, me)
    await client.disconnect()


async def run_session(path: str) -> None:
    from seshforge import Client

    client = await Client.from_session_file(path, API_ID, API_HASH)
    me = await client.get_me()
    _print_result(client.session_string, me)
    await client.disconnect()


async def run_string(value: str) -> None:
    from seshforge import Client

    client = await Client.from_string(value, API_ID, API_HASH)
    me = await client.get_me()
    _print_result(client.session_string, me)
    await client.disconnect()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="seshforge",
        description="Forge Telethon StringSessions from tdata / .session / string (lock-free runtime)",
    )
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--tdata", metavar="PATH", help="Telegram Desktop tdata directory")
    g.add_argument("--session", metavar="PATH", help="Telethon .session file")
    g.add_argument("--string", metavar="STR", help="existing StringSession to verify/reprint")
    p.add_argument("--account", type=int, default=0, help="tdata account index (default 0)")
    return p


async def async_main() -> None:
    args = build_parser().parse_args()
    if args.tdata:
        await run_tdata(args.tdata, args.account)
    elif args.session:
        await run_session(args.session)
    else:
        await run_string(args.string)


def main() -> None:
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\ncanceled", file=sys.stderr)
        raise SystemExit(130) from None


if __name__ == "__main__":
    main()
