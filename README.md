# Event Collection and Delivery Service

The Event Collection and Delivery Service is a FastAPI-based application that collects event payloads and delivers them to specified ports. This README provides an overview of the project design, structure & endpoints.



## Design

The Event Collection and Delivery Service is designed to collect event payloads and deliver them to specified ports using threads. The application utilizes FastAPI for creating RESTful APIs, Redis for storing and managing payload data and threading for parallel processing of payload delivery.



## Structure

- `main.py`: The main entry point of the FastAPI application.
- `routes.py`: Defines the API routes using FastAPI, including the `/collect_api`, `/start_delivery`, and `/stop_delivery` endpoints.
- `delivery_thread.py`: Contains the `DeliveryThread` class responsible for delivering payloads to specified ports using threads.
- `logger.py`: Provides logging utilities for the application.



## API Endpoints

- `/collect_api`: POST endpoint for collecting event payloads. Requires `user_id` and `payload` fields in the JSON payload.
- `/start_delivery`: POST endpoint for starting payload delivery to a specified port.
- `/stop_delivery`: POST endpoint for stopping all payload delivery threads.
