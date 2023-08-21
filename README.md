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
| /start_delivery?port=5555    | a thread is spawned. It stores its delivery state in Redis.     |  `port_5555_deliverd = 0`  |
| /collect_api payload=p1    |   thread:port_5555 which is already active, attempts to deliver p1 to 55555   |   `port_5555_deliverd = 1` <br> `sequence_number = 1` <br> `delivery_requests = [p1]`   |
| /collect_api payload=p2   | thread:port_5555 which is already active, attempts to deliver p2 to 55555    |  `port_5555_deliverd = 2` <br> `sequence_number = 2` <br> `delivery_requests = [p1, p2]`     |
| /start_delivery?port=6666  |  A new thread is spawned, it needs to deliver from the next incoming request. It stores its status number by retrieving current value of sequence_number  |  `port_5555_deliverd = 2` <br> `port_6666_deliverd = 2` <br> `delivery_requests = [p1, p2]` |
| /collect_api payload=p3   | thread:port_5555, thread:port_6666 which are already active, attempts to deliver p3 to 55555, 6666    |  `port_5555_deliverd = 3` <br> `port_6666_deliverd = 3` <br> `sequence_number = 3` <br> `delivery_requests = [p1, p2, p3]`     |
| /start_delivery?port=7777  |  Let's assume, the port is not listening and does not accept any requests  |  `port_5555_deliverd = 3` <br> `port_6666_deliverd = 3` <br>`port_7777_deliverd = 3` <br> `sequence_number = 3` <br> `delivery_requests = [p1, p2, p3]` |
| /collect_api payload=p4   | thread:port_5555, thread:port_6666 which are already active, attempts to deliver p3 to 55555, 6666. thread:port_7777 also starts it work to deliver the payload to 7777. But 7777 is not ready to accept or is down   |  `port_5555_deliverd = 4` <br> `port_6666_deliverd = 4` <br> `port_7777_deliverd = ?` <br> `sequence_number = 4` <br> `delivery_requests = [p1, p2, p3, p4]`   <br> ? => After trying for 3 times (with a wait of 1 second each time), the system compromises on this request and logs it, and updates `port_7777_deliverd` to value 4  |



## Structure

- `main.py`: The main entry point of the FastAPI application.
- `routes.py`: Defines the API routes using FastAPI, including the `/collect_api`, `/start_delivery`, and `/stop_delivery` endpoints.
- `delivery_thread.py`: Contains the `DeliveryThread` class responsible for delivering payloads to specified ports using threads.
- `logger.py`: Provides logging utilities for the application.


## Let's talk Test cases

- `test_collect_api.py`
  - `test_postive_collect_api`: hits the /collect endpoint with a payload & checks if the sequence_number is incremented & stored in Redis.
  - `test_negative_collect_api`: when /collect endpoint is hit with improper payload, the API should respond with a 400 error status.

- `test_start_delivery.py`
  - `test_start_delivery_and_check_threads`: when /start_delivery endpoint is hit along with a port number parameter, a thread has to be spawned. We are testing if any new threads are created here once the endpoint is hit.
  - `test_start_delivery_and_check_redis`:  when /start_delivery endpoint is hit along with a port number parameter, a thread has to be spawned and it has to store its delivery status in the Redis cache. Here we are checking whether the Redis status for the thread is set.
 
- `test_post_payload.py`
  - `test_positive_post_the_payload`: when a thread is actively running & is waiting to deliver any arrived payloads at /collect_api endpoint, it immediately delivers the payload to the destination port. Here we are spawning a thread to deliver to a port, then hitting the /collect_api with a payload & checking whether the running thread is able to make a post request. We mock the actual delivery and just check if the post request is called.
  - `test_positive_retry_post_the_payload`: any payload delivery is retried three times as set in the config file. Here we are trying to check if the destination port has rejected payload acceptance for the first time, and whether our delivery thread is retrying and trying to deliver for a second time.
  - `test_negative_post_the_payload`: after exhausting the set number of attempts, the program must raise a requests.RequestException. Here we are not mocking the request post method & willingly trying to make the payload delivery fail and then trying to check if an exception is raised by asserting like self.assertRaises(RequestException)



