import shutil
import subprocess

from app.services.browser_agent.opencli_command_builder import build_doctor_command


def check_opencli_health(timeout_seconds: int = 15) -> dict:
    executable = shutil.which("opencli")
    if not executable:
        return {
            "installed": False,
            "doctor_ok": False,
            "message": "OpenCLI is not installed. Please run npm install -g @jackwener/opencli and opencli doctor.",
            "raw_output": "",
        }
    completed = subprocess.run(
        build_doctor_command(),
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
        shell=False,
    )
    raw_output = "\n".join(part for part in [completed.stdout, completed.stderr] if part)
    return {
        "installed": True,
        "doctor_ok": completed.returncode == 0,
        "message": "OpenCLI doctor passed." if completed.returncode == 0 else "OpenCLI doctor failed.",
        "raw_output": raw_output,
    }
