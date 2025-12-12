import platform
import subprocess
import sys
import os
import ssl
from pathlib import Path

class CertManager:
    def __init__(self):
        self.cert_dir = Path.home() / ".alpha_axiom" / "certs"
        self.cert_path = self.cert_dir / "localhost.pem"
        self.key_path = self.cert_dir / "localhost-key.pem"
        self._ensure_dir()

    def _ensure_dir(self):
        if not self.cert_dir.exists():
            self.cert_dir.mkdir(parents=True)

    def get_ssl_context(self):
        """Returns an SSL context with the localhost cert loaded."""
        if not self.cert_path.exists() or not self.key_path.exists():
            print("🔐 No certificates found. Generating self-signed for localhost...")
            self._generate_self_signed()
        
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(self.cert_path, self.key_path)
        return ssl_context

    def _generate_self_signed(self):
        """
        Generates a self-signed cert for localhost.
        NOTE: Browsers will warn about this unless trusted manually.
        For MVP, user accepts 'Proceed to unsafe'.
        For Prod, use mkcert via subprocess.
        """
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        import datetime

        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
        ])

        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
            critical=False,
        ).sign(key, hashes.SHA256())

        # Write Key
        with open(self.key_path, "wb") as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))

        # Write Cert
        with open(self.cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        print(f"✅ Certificates generated at {self.cert_dir}")
