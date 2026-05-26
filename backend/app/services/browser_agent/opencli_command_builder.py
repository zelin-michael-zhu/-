def build_doctor_command() -> list[str]:
    return ["opencli", "doctor"]


def build_open_command(session: str = "applypilot", url: str = "") -> list[str]:
    return ["opencli", "browser", session, "open", url]


def build_state_command(session: str = "applypilot") -> list[str]:
    return ["opencli", "browser", session, "state"]


def build_click_command(session: str = "applypilot", target: str = "") -> list[str]:
    return ["opencli", "browser", session, "click", target]


def build_fill_command(session: str = "applypilot", field: str = "", value: str = "") -> list[str]:
    return ["opencli", "browser", session, "fill", field, value]


def build_type_command(session: str = "applypilot", text: str = "") -> list[str]:
    return ["opencli", "browser", session, "type", text]


def build_select_command(session: str = "applypilot", field: str = "", value: str = "") -> list[str]:
    return ["opencli", "browser", session, "select", field, value]


def build_extract_command(session: str = "applypilot", instruction: str = "") -> list[str]:
    return ["opencli", "browser", session, "extract", instruction]


def build_screenshot_command(session: str = "applypilot") -> list[str]:
    return ["opencli", "browser", session, "screenshot"]


def build_wait_command(session: str = "applypilot", condition: str = "") -> list[str]:
    return ["opencli", "browser", session, "wait", condition]


def build_close_command(session: str = "applypilot") -> list[str]:
    return ["opencli", "browser", session, "close"]
