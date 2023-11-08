"""Client to call locally running Nagini server"""
from typing import Literal
import dataclasses
import re
import zmq

DEFAULT_CLIENT_SOCKET = "tcp://localhost:5555"

_context = zmq.Context()
_socket = _context.socket(zmq.REQ)
_socket.connect(DEFAULT_CLIENT_SOCKET)


@dataclasses.dataclass
class VerificationResult:
    """Result of verification"""

    status: Literal[
        "Verification successful",
        "Runtime Error",
        "Verification failed",
        "Translation failed",
    ]
    errors: str | None = (
        None  # None if status is "Verification successful" or "Runtime Error"
    )
    line_no: str | None = (
        None  # None if status is "Verification successful" or "Runtime Error"
    )

    def __str__(self) -> str:
        if self.status == "Verification failed":
            return f"Verification failed: {self.errors} at line {self.line_no}"
        if self.status == "Translation failed":
            return f"Translation failed: {self.errors} at line {self.line_no}"
        return self.status


def verify(file: str) -> VerificationResult:
    """Returns a list of verification errors for the given file or success"""

    _socket.send_string(file)
    response: list[str] = _socket.recv_string().split("\n")
    print("response", response)
    if response[0] == "Runtime Error":
        return VerificationResult("Runtime Error")
    assert len(response) >= 3
    assert response[0] == "" and (
        response[-1].startswith("Verification took")
        or response[1] == "Translation failed"
    )

    if response[1] == "Verification successful":
        assert len(response) == 3
        return VerificationResult("Verification successful")

    if response[1] == "Verification failed":
        assert len(response) > 4 and response[2] == "Errors:"
        # return "Errors:\n" + "\n".join(response[3:-1])
        msg, line_no = _parse_error_message(response[3])
        return VerificationResult("Verification failed", msg, line_no)

    if response[1] == "Translation failed":
        msg, line_no = _parse_error_message(response[2])
        return VerificationResult("Translation failed", msg, line_no)

    raise ValueError(f"Unexpected response from Nagini: {response}")


def _parse_error_message(error_message: str) -> tuple[str, str]:
    """Separates the message from the line number"""
    # match the last parantheses in the error message
    match = re.search(r"\(([^)]+)\)$", error_message)
    if match:
        line_no = match.group(1).split("@")[-1]
        message = error_message[: match.start()].strip()
        return (message, line_no)
    # If there's no match, return the entire error message and arbitrary line number
    return (error_message, "0.0")


# verify("/home/omkar/ethz/hs23/thesis/llms-for-verified-programs/nagini_examples/tmp.py")
