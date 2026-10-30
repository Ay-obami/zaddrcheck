# zaddrcheck — Zcash address checker CLI

A Python 3.10+ CLI for validating Zcash transparent, Sapling and Unified address encodings. No external dependencies or wallet/network access are required.

## Run

```sh
./zaddrcheck 't1goiSyw2JinFCmUnfiwwp72LEZzD42TyYu'
# {"input":"t1goiSyw2JinFCmUnfiwwp72LEZzD42TyYu","valid":true,"type":"transparent"}

./zaddrcheck 'not-an-address'
# {"input":"not-an-address","valid":false,"type":"invalid"}

./zaddrcheck ''
# {"input":"","valid":false,"type":"invalid"}
```

Alternatively, run `python3 zaddrcheck <address>`. The CLI emits **exactly one JSON object per invocation** with keys `input` (original input), `valid` (JSON boolean), and `type` (`transparent`, `sapling`, `unified`, or `invalid`). Missing or malformed input returns an invalid result without crashing; no extra logging contaminates stdout.

## Checks performed

- **Transparent (`t1`, `t3`, `tm`, `t2`)** — Mainnet/testnet P2PKH and P2SH, Base58 alphabet, decoded byte length, Zcash version prefix, double-SHA256 Base58Check checksum.
- **Sapling (`zs1` and test/regtest HRPs)** — Bech32 checksum (not Bech32m), known HRP, canonical bit conversion, 43-byte address payload, uppercase accepted but mixed case rejected.
- **Unified (`u1`, `utest1`, `uregtest1`)** — ZIP-316 Revision 0: Bech32m checksum, F4Jumble inverse with BLAKE2b personalization, HRP padding verification, canonical CompactSize fields, receiver length and ordering validation, no duplicate/conflicting transparent receivers, and a required shielded receiver.
- Rejects altered checksums, malformed/truncated encodings, invalid characters, empty input, and stray whitespace. Prefix matching alone never establishes validity.

These checks validate *address encodings*, not wallet ownership. Full shielded-group point validation is outside this dependency-free CLI and should be performed by a Zcash wallet library prior to sending funds. Proposed ZIP-316 Revision 2 prefixes are not supported here.

## Test suite and CI

```sh
python3 -m unittest discover -s tests -v
```

Tests cover real public Zcash address samples (P2PKH, P2SH, Sapling, Unified and several UA receiver combinations), invalid checksums, mixed case, empty/malformed inputs, and the exact CLI JSON contract. GitHub Actions runs the tests and CLI smoke checks on the default `main` branch and pull requests.

## References

- [Zcash protocol](https://zips.z.cash/protocol/protocol.pdf)
- [ZIP 173: Bech32](https://zips.z.cash/zip-0173)
- [ZIP 316: Unified Addresses](https://zips.z.cash/zip-0316)
