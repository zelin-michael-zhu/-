def detects_captcha_or_login(snapshot_text: str | None) -> tuple[bool, bool]:
    lowered = (snapshot_text or "").lower()
    login = any(keyword in lowered for keyword in ["login", "sign in", "password", "登录", "密码"])
    captcha = any(keyword in lowered for keyword in ["captcha", "recaptcha", "verification code", "验证码"])
    return login, captcha
