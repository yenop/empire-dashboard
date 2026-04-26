#!/usr/bin/env python3
"""Generate Argon2 hash for EMPIRE_PASSWORD_HASH. Usage:
   cd backend && python ../scripts/hash_password.py 'your password'
   Requires: pip install passlib[argon2] argon2-cffi
"""
import getpass
import sys

from passlib.context import CryptContext

ctx = CryptContext(schemes=["argon2"], deprecated="auto")


def main() -> None:
    if len(sys.argv) >= 2:
        password = sys.argv[1]
    else:
        password = getpass.getpass("Password: ")
    if not password:
        print("Empty password", file=sys.stderr)
        sys.exit(1)
    print(ctx.hash(password))


if __name__ == "__main__":
    main()
