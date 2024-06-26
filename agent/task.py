
GRANTED = "granted"
DENIED = "denied"
INSUFFICIENT = "insufficient"
FAILED = "failed"

class Task:
    target: str

    def __init__(self, target="") -> None:
        self.target = target

    def set_target(self, target: str) -> None:
        self.target = target

    def get_target(self) -> str:
        return self.target
    
    def copy(self) -> "Task":
        return Task(self.target)

class Result:
    status: str
    message: str
    def granted(self, message: str) -> "Result":
        self.status = GRANTED
        self.message = message
        return self
    
    def denied(self, message: str) -> "Result":
        self.status = DENIED
        self.message = message
        return self

    def insufficient(self, message: str) -> "Result":
        self.status = INSUFFICIENT
        self.message = message
        return self

    def failed(self, message: str) -> "Result":
        self.status = FAILED
        self.message = message
        return self

    def is_granted(self):
        return self.status == GRANTED
    
    def is_denied(self):
        return self.status == DENIED
    
    def is_insufficient(self):
        return self.status == INSUFFICIENT
    
    def is_failed(self):
        return self.status == FAILED
    
def is_denied(status: str):
    return status == DENIED

def is_granted(status: str):
    return status == GRANTED

def is_insufficient(status: str):
    return status == INSUFFICIENT

def is_failed(status: str):
    return status == FAILED