
```markdown
# WPS Reverse-Engineered RSA Crypto

A standalone Python module replicating the core RSA encryption logic extracted from a specific WPS target. This script demonstrates how the target application handles payload encryption with dynamic hashing fallbacks based on RSA key size constraints.

## 🔍 How It Works

During the reverse engineering process, it was discovered that the target application does not strictly encrypt raw plaintext passwords. Instead, it tests the payload against the RSA key size limit (using PKCS#1 v1.5 padding, which requires an 11-byte overhead). 

It iteratively attempts the following strategies until one fits the public key constraints:
1. Raw Plaintext (`utf-8`)
2. SHA-256 (Raw Bytes)
3. SHA-256 (Hex String)
4. MD5 (Raw Bytes)
5. MD5 (Hex String)

## 🚀 Installation

Clone the repository and install the required dependencies:

```bash
git clone [https://github.com/yourusername/wps-crypto-re.git](https://github.com/yourusername/wps-crypto-re.git)
cd wps-crypto-re
pip install -r requirements.txt

```

## 🛠 Usage

You can run the script directly for a quick test using the built-in dummy key:

```bash
python wps_crypto.py

```

**To integrate into your own tools:**

```python
from wps_crypto import load_public_key, encrypt_payload

# Load your extracted public key (PEM or Base64 string)
pub_key_str = "YOUR_BASE64_OR_PEM_KEY"
pub_key = load_public_key(pub_key_str)

# Encrypt the password
encrypted_b64 = encrypt_payload(pub_key, "target_password_123")
print(encrypted_b64)

```

## ⚠️ Disclaimer

This project is for educational and security research purposes only. The author is not responsible for any misuse of this code.

```

```