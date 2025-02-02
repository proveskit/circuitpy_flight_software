class Radio:
    def __init__(self):
        pass

    def send_message(self, message: str) -> None:
        raise NotImplementedError("send_message must be implemented by subclasses")

    def receive_message(self) -> str:
        raise NotImplementedError("receive_message must be implemented by subclasses")
