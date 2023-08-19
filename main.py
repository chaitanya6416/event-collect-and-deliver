from fastapi import FastAPI
from routes import setup_routes
from uvicorn import run

app = FastAPI()


setup_routes(app)


if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000)
