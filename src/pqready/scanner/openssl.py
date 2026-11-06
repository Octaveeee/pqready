import subprocess


def run_s_client(host: str, port: int, args: list[str], timeout: float) -> str:
    """Run openssl s_client against host:port and return its combined output."""
    command = ["openssl", "s_client", "-connect", f"{host}:{port}", *args]
    try:
        result = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
            errors="replace",
        )
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(f"openssl s_client timed out after {timeout}s on {host}:{port}") from exc
    return result.stdout
