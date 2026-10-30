"""Real-world Zcash fixtures and negative address-validation tests."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from zaddrcheck_core import classify, _decode_bech32, _f4jumble_inverse

T1 = "t1goiSyw2JinFCmUnfiwwp72LEZzD42TyYu"
T3 = "t3ev37Q2uL1sfTsiJQJiWJoFzQpDhmnUwYo"
ZS = "zs1cpf4prtmnqpg6x2ngcrwelu9a39z9l9lqukq9fwagnaqrknk34a7n3szwxpjuxfjdxkuzykel53"
U1 = "u1cysntkxwt0h4sahp7rhj7u27pgc2ga7685ekf65g0d5ht5glkfm4zkumhvkd2zg2pdrgv3mrwq2x3vw2yl5u7zef3cr2nqwrzu7v2dsa"
U_TS = "u13qutpuktq026dwczvxmnh8mxdacsjx3kg2rrhzgns8zsty53t9y0hqp5d440zc9w7z7zkkjqw8dq0uuc0mkt883464mq8mkys7l4xjnhylh7u3u02ukknurm5yxerqlf500y2atq28e"
U_TO = "u1yvwppp7ann6n3pgkysdu0spvr50w4jf4jwgme3c8x8fp4av59rupgvdd3fddc3f2cwrk3ghs5lxt87ggj8cvjuzcrf4jkejwlu9pc83gk2vtx03ucqcc3ed0furcuypqs6d6swu3nws"
U_SO = "u1dq8kg78fgpjsc7dn2ynpdzc8xu99wra0jec4jy30rjqk5frsj62qtgqcu9nn0j8g352phlwprshancgxcuhdcclx0wxtvqylhmuegas7ul8hwnwggy727l05pyujuywtnn4nkfznctaelpkcrqcm9cxhkgv3t9jtrvgym7la5varrmzc"


class CheckerTests(unittest.TestCase):
    def assertValid(self, address, kind):
        self.assertEqual(classify(address), {"input": address, "valid": True, "type": kind})

    def assertInvalid(self, address):
        self.assertEqual(classify(address), {"input": address, "valid": False, "type": "invalid"})

    def test_valid_transparent(self):
        for address in (T1, T3):
            self.assertValid(address, "transparent")

    def test_valid_sapling(self):
        self.assertValid(ZS, "sapling")
        self.assertValid(ZS.upper(), "sapling")

    def test_valid_unified(self):
        for address in (U1, U_TS, U_TO, U_SO, U1.upper()):
            self.assertValid(address, "unified")

    def test_changed_checksum(self):
        for address in (T1, T3, ZS, U1, U_TS):
            altered = address[:-1] + ("q" if address[-1] != "q" else "p")
            self.assertInvalid(altered)

    def test_malformed_and_empty(self):
        for address in ("", " ", "notAnAddress", "t1invalid", "zs1invalid",
                        "u1invalid", "u1", "t123", "zcUexample", "0" * 10000,
                        "u1" + "q" * 1000, "not❄ascii", "😊"):
            self.assertInvalid(address)

    def test_case_and_whitespace(self):
        self.assertInvalid(ZS[:10].upper() + ZS[10:])
        self.assertInvalid(U1[:10].upper() + U1[10:])
        self.assertInvalid(ZS + " ")
        self.assertInvalid(" " + T1)

    def test_not_prefix_only(self):
        self.assertInvalid("t1" + "a" * 33)
        self.assertInvalid("zs1" + "q" * 75)
        self.assertInvalid("u1" + "q" * 120)

    def test_real_unified_payload(self):
        hrp, variant, payload = _decode_bech32(U1)
        self.assertEqual((hrp, variant), ("u", 0x2BC830A3))
        self.assertTrue(_f4jumble_inverse(payload).endswith(b"u" + b"\0" * 15))

    def test_cli_stdout_contract(self):
        process = subprocess.run([str(ROOT / "zaddrcheck"), T1], capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(process.stdout), classify(T1))
        self.assertEqual(process.stderr, "")
        self.assertEqual(len(process.stdout.splitlines()), 1)

    def test_empty_cli_does_not_crash(self):
        for args in ([], ["bad"], [""]):
            process = subprocess.run([str(ROOT / "zaddrcheck"), *args], capture_output=True, text=True, check=True)
            self.assertFalse(json.loads(process.stdout)["valid"])
            self.assertEqual(process.stderr, "")


if __name__ == "__main__":
    unittest.main()
