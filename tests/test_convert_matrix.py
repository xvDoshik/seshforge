import base64
import struct
import tempfile
import unittest
from pathlib import Path

from telethon.crypto import AuthKey
from telethon.sessions import StringSession

from seshforge import (
    AuthParts,
    __version__,
    detect_string_kind,
    memory_from_parts,
    pack_pyrogram_string,
    pyrogram_string_to_telethon_string,
    session_to_string,
    string_to_pyrogram_file,
    string_to_session,
    string_to_session_file,
    telethon_string_from_parts,
    telethon_string_to_pyrogram_string,
    unpack_pyrogram_string,
)
from seshforge.convert import DC_IPV4, session_file_to_string
from seshforge.pyro_session import pyrogram_file_to_pyrogram_string, pyrogram_file_to_string


def _fake_auth_key() -> bytes:
    return bytes(range(256))


def _telethon_string() -> str:
    ss = memory_from_parts(2, DC_IPV4[2], 443, _fake_auth_key())
    return session_to_string(ss)


class ConvertMatrixTests(unittest.TestCase):
    def test_version(self):
        self.assertEqual(__version__, "0.2.0")

    def test_telethon_roundtrip_parts(self):
        tl = _telethon_string()
        self.assertEqual(detect_string_kind(tl), "telethon")
        parts = AuthParts(dc_id=2, auth_key=_fake_auth_key(), server_address=DC_IPV4[2], port=443)
        rebuilt = telethon_string_from_parts(parts)
        ss = StringSession(rebuilt)
        self.assertEqual(ss.dc_id, 2)
        self.assertEqual(ss.auth_key.key, _fake_auth_key())

    def test_telethon_file_roundtrip(self):
        tl = _telethon_string()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "acc.session"
            out = string_to_session_file(tl, path)
            self.assertTrue(out.exists())
            back = session_file_to_string(out)
            a = StringSession(tl)
            b = StringSession(back)
            self.assertEqual(a.dc_id, b.dc_id)
            self.assertEqual(a.auth_key.key, b.auth_key.key)

    def test_pyrogram_pack_unpack(self):
        parts = AuthParts(
            dc_id=2,
            auth_key=_fake_auth_key(),
            api_id=12345,
            user_id=999001,
            is_bot=False,
            test_mode=False,
        )
        pyro = pack_pyrogram_string(parts)
        self.assertEqual(detect_string_kind(pyro), "pyrogram")
        back = unpack_pyrogram_string(pyro)
        self.assertEqual(back.dc_id, 2)
        self.assertEqual(back.auth_key, _fake_auth_key())
        self.assertEqual(back.api_id, 12345)
        self.assertEqual(back.user_id, 999001)

    def test_telethon_pyrogram_string_bridge(self):
        tl = _telethon_string()
        pyro = telethon_string_to_pyrogram_string(tl, api_id=2040, user_id=42, is_bot=False)
        self.assertEqual(detect_string_kind(pyro), "pyrogram")
        tl2 = pyrogram_string_to_telethon_string(pyro)
        a = StringSession(tl)
        b = StringSession(tl2)
        self.assertEqual(a.dc_id, b.dc_id)
        self.assertEqual(a.auth_key.key, b.auth_key.key)

    def test_string_to_session_auto_detect(self):
        tl = _telethon_string()
        pyro = telethon_string_to_pyrogram_string(tl, api_id=1, user_id=7)
        self.assertIsInstance(string_to_session(tl), StringSession)
        self.assertIsInstance(string_to_session(pyro), StringSession)

    def test_pyrogram_file_roundtrip(self):
        tl = _telethon_string()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pyro.session"
            out = string_to_pyrogram_file(
                tl, path, api_id=2040, user_id=1001, is_bot=False
            )
            self.assertTrue(out.exists())
            tl2 = pyrogram_file_to_string(out)
            a = StringSession(tl)
            b = StringSession(tl2)
            self.assertEqual(a.auth_key.key, b.auth_key.key)
            pyro = pyrogram_file_to_pyrogram_string(out)
            self.assertEqual(detect_string_kind(pyro), "pyrogram")
            packed = base64.urlsafe_b64decode(pyro + "=" * (-len(pyro) % 4))
            self.assertEqual(len(packed), struct.calcsize(">BI?256sQ?"))

    def test_memory_session_auth_key_type(self):
        ss = memory_from_parts(1, DC_IPV4[1], 443, _fake_auth_key())
        self.assertIsInstance(ss.auth_key, AuthKey)


if __name__ == "__main__":
    unittest.main()
