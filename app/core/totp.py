import pyotp
import qrcode
from io import BytesIO
import base64

def generate_totp_secret() -> str:
    """Gera um secret para TOTP"""
    return pyotp.random_base32()

def generate_totp_uri(secret: str, email: str, issuer: str = "Sentinela") -> str:
    """Gera URI para configurar TOTP no aplicativo autenticador"""
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=email,
        issuer_name=issuer
    )

def generate_qr_code(uri: str) -> str:
    """Gera QR Code em base64 a partir da URI"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

def verify_totp(secret: str, token: str) -> bool:
    """Verifica se o token TOTP é válido"""
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=1)
