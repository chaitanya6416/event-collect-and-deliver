from fastapi import FastAPI
from uvicorn import run
from routes import setup_routes


app = FastAPI()
setup_routes(app)


if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000)
