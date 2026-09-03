import hashlib
import hmac
import urllib.parse
from typing import Optional
from app.config import settings


def validate_telegram_webapp(initData: str) -> Optional[dict]:
    try:
        parsed = urllib.parse.parse_qs(initData)
        hash_val = parsed.get("hash", [None])[0]
        if not hash_val:
            return None

        data_check = []
        for key, val in sorted(parsed.items()):
            if key != "hash":
                data_check.append(f"{key}={val[0]}")

        data_check_string = "\n".join(data_check)

        secret_key = hmac.new(
            b"WebAppData",
            settings.BOT_TOKEN.encode(),
            hashlib.sha256,
        ).digest()

        computed_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256,
        ).hexdigest()

        if computed_hash != hash_val:
            return None

        result = {}
        for key, val in parsed.items():
            result[key] = val[0] if len(val) == 1 else val

        user_data = result.get("user")
        if user_data:
            import json
            result["user"] = json.loads(user_data)

        return result
    except Exception:
        return None
