# Event Collection and Delivery Service

The Event Collection and Delivery Service is a FastAPI-based application that collects event payloads and delivers them to destinations (for the simplicity of implementation, the destinations here in the project are just the local machine HTTP ports). This README provides an overview of the project design, structure & endpoints.

## Design

<img src="https://github.com/chaitanya6416/event-collect-and-deliver/assets/36512605/6df0f01c-b5e0-4c7d-a2d1-c72d5ab3c4cb" alt="collect-deliver" width="75%" height="75%">



The Event Collection and Delivery Service is designed to collect event payloads and deliver them to specified ports using threads. The application utilizes FastAPI for creating RESTful APIs, Redis for storing and managing payload data and threading for parallel processing of payload delivery.


## API Endpoints

- `/collect_api`: POST endpoint for collecting event payloads. Requires `user_id` and `payload` fields in the JSON payload.
- `/start_delivery`: POST endpoint for starting payload delivery to a specified port.
- `/stop_delivery`: POST endpoint for stopping all payload delivery threads.

## Let's Simulate

| Endpoint | Action that takes place | Redis Snapshot at the moment |
|-----------------|-----------------|-----------------|
| /start_delivery?port=5555    | a thread is spawned. It stores its delivery state in Redis.     |  `thread_5555_deliverd = 0`  |
| /collect_api payload=p1    |   thread_5555 which is already active, attempts to deliver p1 to 55555   |   `thread_5555_deliverd = 1` <br> `sequence_number = 1` <br> `delivery_requests = [p1]`   |
| /collect_api payload=p2   | thread_5555 which is already active, attempts to deliver p2 to 55555    |  `thread_5555_deliverd = 2` <br> `sequence_number = 2` <br> `delivery_requests = [p1, p2]`     |
| /start_delivery?port=6666  |  A new thread is spawned, it needs to deliver from the next incoming request. It stores its status number by retrieving current value of sequence_number  |  `thread_5555_deliverd = 2` <br> `thread_6666_deliverd = 2` <br> `delivery_requests = [p1, p2]` |
| /collect_api payload=p3   | thread_5555, thread_6666 which are already active, attempts to deliver p3 to 55555, 6666    |  `thread_5555_deliverd = 3` <br> `thread_6666_deliverd = 3` <br> `sequence_number = 3` <br> `delivery_requests = [p1, p2, p3]`     |
| /start_delivery?port=7777  |  Let's assume, the port is not listening and does not accept any requests  |  `thread_5555_deliverd = 3` <br> `thread_6666_deliverd = 3` <br>`thread_7777_deliverd = 3` <br> `sequence_number = 3` <br> `delivery_requests = [p1, p2, p3]` |
| /collect_api payload=p4   | thread_5555, thread_6666 which are already active, attempts to deliver p3 to 55555, 6666    |  `thread_5555_deliverd = 4` <br> `thread_6666_deliverd = 4` <br> `thread_7777_deliverd = ?` <br> `sequence_number = 4` <br> `delivery_requests = [p1, p2, p3, p4]`   <br> ? => after trying for 3 times (with a wait of 1 second each time), system compromises on this request and logs it, and updates `thread_7777_deliverd` to value 4  |



## Structure

- `main.py`: The main entry point of the FastAPI application.
- `routes.py`: Defines the API routes using FastAPI, including the `/collect_api`, `/start_delivery`, and `/stop_delivery` endpoints.
- `delivery_thread.py`: Contains the `DeliveryThread` class responsible for delivering payloads to specified ports using threads.
- `logger.py`: Provides logging utilities for the application.




