from app.services.browser_agent.opencli_command_builder import (
    build_doctor_command,
    build_fill_command,
    build_open_command,
    build_state_command,
)


def test_build_doctor_command():
    command = build_doctor_command()
    assert command == ["opencli", "doctor"]
    assert isinstance(command, list)


def test_build_open_command():
    command = build_open_command("applypilot", "https://example.com")
    assert command == ["opencli", "browser", "applypilot", "open", "https://example.com"]
    assert isinstance(command, list)


def test_build_state_command():
    command = build_state_command("applypilot")
    assert command == ["opencli", "browser", "applypilot", "state"]
    assert isinstance(command, list)


def test_build_fill_command():
    command = build_fill_command("applypilot", "first_name", "Zeklin")
    assert command == ["opencli", "browser", "applypilot", "fill", "first_name", "Zeklin"]
    assert isinstance(command, list)
