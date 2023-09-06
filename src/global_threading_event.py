import threading

# Shared event object
_shared_event = threading.Event()


class GlobalThreadingEvent():
    def __init__(self):
        self._event = _shared_event
