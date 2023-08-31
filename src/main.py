import config
import signal
from fastapi import FastAPI
from uvicorn import run
from routes import setup_routes


app = FastAPI()
setup_routes(app)


def handle_shutdown(signum, frame):
    for thread in config.delivery_threads:
        thread.stop()
        thread.join()
    config.delivery_threads.clear()


def setup_signal_handling():
    signal.signal(signal.SIGINT, handle_shutdown)


if __name__ == "__main__":
    setup_signal_handling()
    run(app, host="0.0.0.0", port=8000, reload=True)
