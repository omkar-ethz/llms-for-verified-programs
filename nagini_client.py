"""Client to call locally running Nagini server"""
import zmq

DEFAULT_CLIENT_SOCKET = "tcp://localhost:5555"


class NaginiWrapper:
    """A wrapper for the Nagini verification tool"""

    def __init__(self):
        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        self.socket.connect(DEFAULT_CLIENT_SOCKET)

    def verify(self, file: str) -> str:
        """Returns a list of verification errors for the given file or success"""

        self.socket.send_string(file)
        response: str = self.socket.recv_string().split("\n")
        print("response", response)
        assert len(response) >= 3
        assert response[0] == "" and response[-1].startswith("Verification took")

        if response[1] == "Verification successful":
            assert len(response) == 3
            return "Verification successful"

        if response[1] == "Verification failed":
            assert len(response) > 4 and response[2] == "Errors:"
            return "Errors:\n" + "\n".join(response[3:-1])

        raise ValueError(f"Unexpected response from Nagini: {response}")
