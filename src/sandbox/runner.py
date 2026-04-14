import subprocess
import sys
import time

from src.utils.config import load_config

def run_file(path):

    config = load_config()
    runner_config = config["runner"]
    timeout = runner_config["TIMEOUT"]

    start = time.time()

    try:
        result = subprocess.run(
            [sys.executable, "-u", str(path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout
        )

        runtime = time.time() - start

        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "runtime": runtime
        }
    except subprocess.TimeoutExpired as e:
        return {
            "exit_code": None,
            "stdout": e.stdout,
            "stderr": "TIMEOUT",
            "runtime": timeout
        }