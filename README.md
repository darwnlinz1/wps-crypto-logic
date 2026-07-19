# WPS Office — Client-Side RSA Crypto (Reverse Engineered)

A standalone Python module that reproduces the client-side password-encryption
logic used by WPS Office. The project is a **security research exercise**: it
documents how the application prepares and encrypts a password before sending it
to the server, and evaluates the design against modern cryptographic best
practices.

> Full technical breakdown: see [`SECURITY_ANALYSIS.md`](./SECURITY_ANALYSIS.md).

## Overview

During analysis it was found that the application does **not** always encrypt the
raw password. Instead it computes the maximum payload size allowed by the RSA
key (PKCS#1 v1.5 padding reserves 11 bytes of overhead) and iterates through a
set of candidate payloads, encrypting the first one that fits:

1. Raw password (UTF-8)
2. SHA-256 (raw bytes)
3. SHA-256 (hex string)
4. MD5 (raw bytes)
5. MD5 (hex string)

The selected payload is encrypted with RSA (PKCS#1 v1.5) and Base64-encoded.

## Requirements

- Python 3.8+
- [`cryptography`](https://pypi.org/project/cryptography/)

## Installation

```bash
git clone https://github.com/darwnlinz1/wps-crypto-logic.git
cd wps-crypto-logic
pip install -r requirements.txt
```

## Usage

Run directly for a quick test using the built-in **dummy** key:

```bash
python wps_crypto.py
```

Use as a module:

```python
from wps_crypto import load_public_key, encrypt_payload

pub_key = load_public_key("YOUR_BASE64_OR_PEM_KEY")
encrypted_b64 = encrypt_payload(pub_key, "target_password")
print(encrypted_b64)
```

## Security Notes

The scheme relies on outdated primitives (PKCS#1 v1.5 padding, MD5 fallback) and
performs no integrity checking. Recommended fixes — RSA-OAEP, ≥2048-bit keys,
authenticated encryption, and never transmitting a raw password — are detailed
in [`SECURITY_ANALYSIS.md`](./SECURITY_ANALYSIS.md).

## Disclaimer

This project is intended for **educational and security research purposes only**.
It contains no real keys and no exploit code. The author is not responsible for
any misuse of this code.
