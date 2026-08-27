import bcrypt


def verify_password(plain_password: str, hashed_password: str) -> bool:
  # Truncate UTF-8 bytes to prevent Bcrypt 72-byte overflow exceptions
  password_bytes = plain_password.encode("utf-8")[:72]
  hashed_bytes = hashed_password.encode("utf-8")
  return bcrypt.checkpw(password_bytes, hashed_bytes)


def get_password_hash(password: str) -> str:
  password_bytes = password.encode("utf-8")[:72]
  salt = bcrypt.gensalt()
  return bcrypt.hashpw(password_bytes, salt).decode("utf-8")