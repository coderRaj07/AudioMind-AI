#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
COMPOSE_FILE = ROOT / "docker" / "docker-compose.yml"
ENV_FILE = ROOT / ".env"
ENV_EXAMPLE = ROOT / ".env.example"
VENV_PYTHON = ROOT / "venv" / "bin" / "python"
PYTHON = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable

processes: list[tuple[str, subprocess.Popen]] = []


def log(message: str) -> None:
    print(f"[start] {message}", flush=True)


def fail(message: str, code: int = 1) -> None:
    print(f"[start] ERROR: {message}", file=sys.stderr, flush=True)
    raise SystemExit(code)


def command_text(command: list[str]) -> str:
    return " ".join(command)


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    log(f"$ {command_text(command)}")
    result = subprocess.run(command, cwd=ROOT, env=child_env())
    if check and result.returncode != 0:
        fail(f"Command failed with exit code {result.returncode}: {command_text(command)}")
    return result


def child_env() -> dict[str, str]:
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(ROOT) if not existing_pythonpath else f"{ROOT}:{existing_pythonpath}"
    return env


def compose_command() -> list[str]:
    if shutil.which("docker"):
        result = subprocess.run(
            ["docker", "compose", "version"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode == 0:
            return ["docker", "compose"]

    if shutil.which("docker-compose"):
        return ["docker-compose"]

    fail("Docker Compose was not found. Install Docker Desktop/Engine with Compose support.")


def ensure_docker_is_running(compose: list[str]) -> None:
    if shutil.which("docker"):
        run(["docker", "info"], check=True)
    else:
        run([*compose, "version"], check=True)


def ensure_required_files() -> None:
    if not COMPOSE_FILE.exists():
        fail(f"Compose file not found: {COMPOSE_FILE}")

    if ENV_FILE.exists():
        return

    if not ENV_EXAMPLE.exists():
        fail(".env is missing and .env.example was not found.")

    shutil.copyfile(ENV_EXAMPLE, ENV_FILE)
    log("Created .env from .env.example. Add real API keys there before using upload/query flows.")


def read_env_file() -> dict[str, str]:
    values: dict[str, str] = {}
    if not ENV_FILE.exists():
        return values

    for raw_line in ENV_FILE.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")

    return values


def wait_for_port(host: str, port: int, name: str, timeout: int = 90) -> None:
    log(f"Waiting for {name} on {host}:{port}...")
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=2):
                log(f"{name} is ready.")
                return
        except OSError:
            time.sleep(2)

    fail(f"Timed out waiting for {name} on {host}:{port}. Check `docker compose ps`.")


def ensure_minio_bucket() -> None:
    env = read_env_file()
    endpoint = env.get("S3_ENDPOINT", "http://localhost:9000")
    access_key = env.get("S3_ACCESS_KEY", "minio")
    secret_key = env.get("S3_SECRET_KEY", "minio123")
    bucket = env.get("S3_BUCKET", "audio-files")

    try:
        import boto3
        from botocore.exceptions import ClientError
    except ImportError:
        log("Skipping MinIO bucket setup because boto3 is not installed.")
        return

    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )

    try:
        client.head_bucket(Bucket=bucket)
        log(f"MinIO bucket already exists: {bucket}")
    except ClientError:
        client.create_bucket(Bucket=bucket)
        log(f"Created MinIO bucket: {bucket}")


def start_process(name: str, command: list[str]) -> None:
    log(f"Starting {name}: {command_text(command)}")
    process = subprocess.Popen(command, cwd=ROOT, env=child_env())
    processes.append((name, process))


def stop_processes() -> None:
    if not processes:
        return

    log("Stopping app processes...")
    for name, process in processes:
        if process.poll() is None:
            log(f"Stopping {name}...")
            process.terminate()

    deadline = time.monotonic() + 10
    for name, process in processes:
        while process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.2)
        if process.poll() is None:
            log(f"Force stopping {name}...")
            process.kill()


def handle_shutdown(signum: int, _frame) -> None:
    log(f"Received signal {signum}. Docker containers will keep running.")
    stop_processes()
    raise SystemExit(0)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Start AudioMind-AI and its Docker services.")
    parser.add_argument("--build", action="store_true", help="Build compose services before starting them.")
    parser.add_argument("--skip-migrations", action="store_true", help="Do not run Alembic migrations.")
    parser.add_argument("--skip-bucket", action="store_true", help="Do not create/check the MinIO bucket.")
    parser.add_argument("--skip-worker", action="store_true", help="Start only the FastAPI server.")
    parser.add_argument("--host", default="0.0.0.0", help="FastAPI host. Default: 0.0.0.0")
    parser.add_argument("--port", default="8000", help="FastAPI port. Default: 8000")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_required_files()

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    compose = compose_command()
    ensure_docker_is_running(compose)

    up_command = [*compose, "-f", str(COMPOSE_FILE), "up", "-d"]
    if args.build:
        up_command.append("--build")
    run(up_command)

    wait_for_port("localhost", 5432, "PostgreSQL")
    wait_for_port("localhost", 9000, "MinIO")
    wait_for_port("localhost", 7233, "Temporal")

    if not args.skip_migrations:
        run([PYTHON, "-m", "alembic", "upgrade", "head"])

    if not args.skip_bucket:
        ensure_minio_bucket()

    if not args.skip_worker:
        start_process("Temporal worker", [PYTHON, "-m", "app.workflows.worker"])

    start_process(
        "FastAPI",
        [
            PYTHON,
            "-m",
            "uvicorn",
            "app.main:app",
            "--reload",
            "--host",
            args.host,
            "--port",
            str(args.port),
        ],
    )

    log(f"App is starting at http://localhost:{args.port}/docs")
    log("Press Ctrl+C to stop the FastAPI app and worker. Docker containers will stay up.")

    try:
        while True:
            for name, process in processes:
                return_code = process.poll()
                if return_code is not None:
                    stop_processes()
                    fail(f"{name} exited with code {return_code}.")
            time.sleep(1)
    finally:
        stop_processes()


if __name__ == "__main__":
    main()
