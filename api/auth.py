"""Authentication utilities"""

import hashlib
import secrets

def hash_password(password, salt=None):
    """
    Hash password with salt
    For production, use bcrypt or argon2
    """
    if salt is None:
        salt = secrets.token_hex(16)
    
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return salt + ':' + pwd_hash.hex()

def verify_password(password, stored_hash):
    """Verify password against stored hash"""
    try:
        salt, pwd_hash = stored_hash.split(':')
        test_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        return test_hash == pwd_hash
    except:
        return False
