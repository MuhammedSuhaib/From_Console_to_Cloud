from pywebpush import Vapid
from cryptography.hazmat.primitives import serialization
import base64

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def generate_vapid_keys_util():
    vapid = Vapid()
    vapid.generate_keys()

    public_key = b64url(
        vapid.public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint,
        )
    )

    private_key = b64url(
        vapid.private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )

    print("Add these to your .env file:")
    print(f"VAPID_PUBLIC_KEY={public_key}")
    print(f"VAPID_PRIVATE_KEY={private_key}")

if __name__ == "__main__":
    generate_vapid_keys_util()
