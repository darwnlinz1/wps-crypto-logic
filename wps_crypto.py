import base64
import hashlib
from typing import Optional

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.backends import default_backend

def load_public_key(pk_str: str) -> RSAPublicKey:
    """Load RSA public key from PEM or Base64 DER format."""
    s = pk_str.strip()
    if s.startswith("-----BEGIN"):
        return serialization.load_pem_public_key(s.encode('utf-8'), backend=default_backend())
    
    try:
        der = base64.b64decode(s, validate=True)
        return serialization.load_der_public_key(der, backend=default_backend())
    except Exception as e:
        raise ValueError(f"Invalid public key format: {e}")

def encrypt_payload(pub_key: RSAPublicKey, password: str) -> Optional[str]:
    """
    Attempt to encrypt the password using reverse-engineered fallback strategies.
    Returns Base64 encoded ciphertext of the first valid payload based on RSA key size.
    """
    # PKCS#1 v1.5 padding requires 11 bytes of overhead
    max_payload = (pub_key.key_size + 7) // 8 - 11  
    pt = password.encode('utf-8')

    # Fallback encryption strategies extracted from target binary
    strategies = [
        pt,
        hashlib.sha256(pt).digest(),
        hashlib.sha256(pt).hexdigest().encode('utf-8'),
        hashlib.md5(pt).digest(),
        hashlib.md5(pt).hexdigest().encode('utf-8'),
    ]

    for payload in strategies:
        if len(payload) > max_payload:
            continue
        try:
            ct = pub_key.encrypt(payload, padding.PKCS1v15())
            return base64.b64encode(ct).decode('utf-8')
        except Exception:
            continue
            
    return None

if __name__ == "__main__":
    # 512-bit dummy RSA public key for out-of-the-box testing
    SAMPLE_PUB_KEY = (
        "-----BEGIN PUBLIC KEY-----\n"
        "MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAJkX+fC5v3Q8V7y1gZ5uQk6/7g+C8b6K\n"
        "t+zH/kKqG3n+tM8Z3b5s7O2YwBq/1Zg9gJ5rXW+2T8o6z3V7Z2wU1Q8CAwEAAQ==\n"
        "-----END PUBLIC KEY-----"
    )
    
    try:
        key = load_public_key(SAMPLE_PUB_KEY)
        target_password = "my_secret_password"
        
        print(f"[*] Target Password: {target_password}")
        result = encrypt_payload(key, target_password)
        
        if result:
            print(f"[+] Encrypted Payload (Base64): {result}")
        else:
            print("[-] Failed to encrypt payload.")
    except Exception as e:
        print(f"[!] Error: {e}")