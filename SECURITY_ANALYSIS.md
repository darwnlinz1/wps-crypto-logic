# Security Analysis — WPS Office Client-Side Encryption

**Document type:** Security research write-up
**Author:** darwnlinz1
**Status:** Public, sensitive material redacted

## 1. Executive Summary

This research analyzes how WPS Office encrypts a user's password on the client
side (on the user's machine) before sending it to the server. The application
uses **RSA with PKCS#1 v1.5 padding** together with an unusual "payload
selection" mechanism: it tries the password in several forms — raw, then MD5 and
SHA-256 hashes — and encrypts the first form that fits within the RSA key-size
limit. This design exposes a few cryptographic weaknesses (outdated padding, no
integrity protection, inconsistent payload logic). This report documents the
analysis method, assesses the risk, and proposes fixes based on modern best
practices.

## 2. Scope & Ethics

- All analysis was performed on software I **installed legally on my own
  machine**, for educational and security-research purposes.
- **No systems were attacked.** No unauthorized access was made to WPS servers or
  to anyone's account.
- This report contains **no real keys, no exploit code, and nothing that aids
  piracy or abuse**. All keys shown are `dummy` placeholders for illustration.
- Goal: demonstrate the ability to read and evaluate a closed cryptographic
  scheme, and to propose how it should be fixed.

## 3. Methodology

- **Environment:** a personal, isolated Windows machine with no impact on other
  systems.
- **Approach:**
  1. Observe the login flow to identify when the password is processed before it
     leaves the client.
  2. Analyze the encryption logic to determine the algorithm, padding type, and
     payload-selection strategy.
  3. Independently reproduce the mechanism with a standalone Python module (using
     the `cryptography` library) to verify understanding — runnable with a
     **dummy public key**, never with WPS's real key.
- **Definition of "understood correctly":** the module reconstructs the exact
  payload format the original application produces, without reusing the original
  binary.

## 4. Technical Findings

**Algorithm:** RSA with **PKCS#1 v1.5** padding.

**Payload selection (the most notable detail):** instead of always encrypting the
raw password, the application computes the maximum size allowed by the RSA key —
for PKCS#1 v1.5 this is `(key_size_in_bytes − 11)` — then tries the following
forms in order and picks the first one that fits:

1. Raw password (UTF-8)
2. SHA-256 (raw bytes)
3. SHA-256 (hex string)
4. MD5 (raw bytes)
5. MD5 (hex string)

**Data flow:**

```
[User password]
        │
        ▼
[Select a payload form that fits the key size]  ← raw → SHA-256 → MD5
        │
        ▼
[RSA encryption / PKCS#1 v1.5 with the public key]
        │
        ▼
[Base64 encoding] ──► sent to the API
```

**Key/IV handling:** an RSA public key is used (the real key is redacted —
`[REDACTED]`). RSA uses no IV. No accompanying symmetric-encryption layer or
integrity check was found.

## 5. Security Assessment

- **PKCS#1 v1.5 padding is outdated.** This padding has a history of *padding
  oracle* vulnerabilities (Bleichenbacher). The modern standard is **RSA-OAEP**.
- **The "try multiple payload forms" logic signals loose design.** Accepting many
  formats makes the system harder to reason about and prone to unexpected
  behavior; a sound scheme should have **one** deterministic payload format.
- **MD5 is still present.** MD5 is considered cryptographically broken; its
  presence (even as a fallback) shows the design has not been modernized.
- **No integrity / authentication.** Plain RSA encryption provides confidentiality
  only; it does **not** prove the data was not tampered with. Authenticated
  encryption is needed.
- **Risk if the key is small.** If the real key is 512–1024 bits, security is very
  low (512-bit RSA is breakable). At least 2048 bits is recommended.
- **Context note:** the transport channel is usually already protected by TLS, so
  this client-side RSA layer is mainly defense-in-depth; done incorrectly it
  easily becomes *security theater* (looks safe without meaningfully increasing
  safety).

## 6. Recommendations

If this were my own application, I would:

1. **Replace PKCS#1 v1.5 with RSA-OAEP (SHA-256).**
2. **Use a single, fixed payload format** — remove the multi-form fallback
   entirely.
3. **Drop MD5.** Use SHA-256 or stronger if hashing is needed.
4. **For larger data, use hybrid encryption:** AES-256-GCM for the data plus
   RSA-OAEP to wrap the AES key — providing both confidentiality and integrity.
5. **Do not authenticate a password by encrypting it directly.** Use a standard
   protocol (server-side hashing with Argon2/bcrypt, or a scheme like SRP) so the
   server never sees the raw password.
6. **Use RSA keys ≥ 2048 bits** with a key-rotation process.

## 7. Conclusion & What I Learned

This exercise built skills in identifying the algorithm and padding of a closed
cryptographic scheme, understanding why PKCS#1 v1.5 and MD5 are considered risky,
and independently reproducing a mechanism to verify understanding without
touching anyone else's systems. The key takeaway: distinguishing "encryption for
show" from genuinely secure encryption — and knowing how to rebuild it to modern
standards.

> *Disclaimer: This document is for educational and security-research purposes
> only. It contains no exploit code, no real keys, and does not aid copyright
> infringement.*
