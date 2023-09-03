# Event Collection and Delivery Service

The Event Collection and Delivery Service is a FastAPI-based application that collects event payloads and delivers them to destinations (for the simplicity of implementation, the destinations here in the project are just the local machine HTTP ports). This README provides an overview of the project design, structure & endpoints.

## Design

<img src="https://github.com/chaitanya6416/event-collect-and-deliver/assets/36512605/6df0f01c-b5e0-4c7d-a2d1-c72d5ab3c4cb" alt="collect-deliver" width="75%" height="75%">



The Event Collection and Delivery Service is designed to collect event payloads and deliver them to specified ports using threads. The application utilizes FastAPI for creating RESTful APIs, Redis for storing and managing payload data and threading for parallel processing of payload delivery.


## API Endpoints

- `/collect_api`: POST endpoint for collecting event payloads. Requires `user_id` and `payload` fields in the JSON payload.
- `/start_delivery`: POST endpoint for starting payload delivery to a specified port.
- `/stop_delivery`: POST endpoint for stopping all payload delivery threads.

## Let's talk deliverables!

| Requirement | what to achieve? | How did we do it? |
|-----------------|-----------------|-----------------|
| Durability | Once an ingested event is accepted, it will remain in the system even if the system crashes or until it is delivered or exhaustively retried. | Two perspectives can arise in the case of durability. (1) system crash & restart (2) Redis crash. <br> (1) The Redis stores the activity status of each delivery thread (the latest payload that is successfully sent). Whenever the system restarts, the system on startup checks the Redis for such information & spawns threads to those destinations and starts the usual thing of delivering payloads. (Find this lifespan events declared here https://github.com/chaitanya6416/event-collect-and-deliver/blob/e4f20ceb7dded2a02c9f31b4bc29e1385017f9c6/src/main.py#L16) <br> (2) Redis supports for RDB and AOF style of backups. The implementation runs a redis_rdb_snapshot every 15 minutes & redis_aof_backup every 1 minute. (to be found here https://github.com/chaitanya6416/event-collect-and-deliver/tree/main/src/backups)|
| At least once delivery| Assume we have minimal control over the supported destinations. Delivery to destinations might fail for any reason, our system needs to retry. | The task of delivering payloads runs with the help of a retry module. We can configure the behavior of this module as required. Like 'time between retries', 'maximum retry count' etc (find it here https://github.com/chaitanya6416/event-collect-and-deliver/blob/e4f20ceb7dded2a02c9f31b4bc29e1385017f9c6/src/delivery_thread.py#L47) |
| Retry backoff and limit| Messages should be retried using a backoff algorithm, after a number of delivery attempts, the event should be drained from the system.| The retry module mentioned above has all these functionalities |
|Maintaining order| Events should be sent in a FIFO method for each destination. | Every delivery thread spawn remembers its delivery state by holding an ID of the last sent payload (can be found here https://github.com/chaitanya6416/event-collect-and-deliver/blob/e4f20ceb7dded2a02c9f31b4bc29e1385017f9c6/src/delivery_thread.py#L90, details about redis stream unique id generation: https://redis.io/docs/data-types/streams/#streams-basics) |
|Delivery Isolation| Delays or failures with event delivery of a single destination should not affect ingestion or other delivery on other destinations. | Every destination registered in the system will be handled by a separate thread. It has its own 'last successful delivery ID', 'list of failed deliveries', etc. which ensures isolation of deliveries between destinations|

## Let's Simulate

| Endpoint | Action that takes place | Redis Snapshot at the moment |
|-----------------|-----------------|-----------------|
| /start_delivery?port=5555    | a thread is spawned. It stores its delivery state in Redis.     |  `last_delivered_m_id_to_5555 = 0`  |
| /collect_api payload=p1    |   thread-to-port-5555 which is already active, attempts to deliver p1 to 5555   |   `last_delivered_m_id_to_5555 = 2023080812034-0` <br> `redis stream = [p1]`   |
| /collect_api payload=p2   | thread-to-port-5555 which is already active, attempts to deliver p2 to 5555    |  `last_delivered_m_id_to_5555 = 2023080812099-0` `redis stream = [p1, p2]`     |
| /start_delivery?port=6666  |  A new thread is spawned, it needs to deliver from the next incoming request. It stores its status from the redis stream info  |  `last_delivered_m_id_to_5555 = 2023080812099-0` <br> `last_delivered_m_id_to_6666 = 2023080812099-0` <br> `delivery_requests = [p1, p2]` |
| /collect_api payload=p3   | thread-to-port-5555, thread-to-port-6666 which are already active, attempts to deliver p3 to 5555, 6666    |  `last_delivered_m_id_to_5555 = 202308081300-0` <br> `last_delivered_m_id_to_6666 = 202308081300-0` <br> `redis stream = [p1, p2, p3]`     |
| /start_delivery?port=7777  |  Let's assume, the port is not listening and does not accept any requests  |  `last_delivered_m_id_to_5555 = 202308081300-0` <br> `last_delivered_m_id_to_6666 = 202308081300-0` <br> `last_delivered_m_id_to_7777 = 202308081300-0` <br> `redis stream = [p1, p2, p3]` |
| /collect_api payload=p4   | thread-to-port-5555, thread-to-port-6666 which are already active, attempts to deliver p3 to 55555, 6666. thread-to-port-7777 also starts its work to deliver the payload to 7777. But 7777 is not ready to accept or is down   |  `last_delivered_m_id_to_5555 = 202308081399-0` <br> `last_delivered_m_id_to_6666 = 202308081399-0` <br> `port_7777_deliverd = ?` <br> `redis stream = [p1, p2, p3, p4]`   <br> ? => After trying say 3 times (with a wait of 1 second each time), the system compromises on this request and stores it, and updates `last_delivered_m_id_to_6666` to value `202308081399-0` which is a value of p4. The system also stores a list of all failed deliveries to each destination, so `failed_m_id_7777 = 202308081399-0` (p4)  |

## Periodic Redis Backups
- Reference: https://redis.io/docs/management/persistence/
- Two types of persistence options:
 - RDB (Redis Database): RDB persistence performs point-in-time snapshots of your dataset at specified intervals.
 - AOF (Append Only File): AOF persistence logs every write operation received by the server. These operations can then be replayed again at server startup, reconstructing the original dataset. Commands are logged using the same format as the Redis protocol itself.
- The implementation runs a redis_rdb_snapshot every 15 minutes & redis_aof_backup every 1 minute. (to be found here https://github.com/chaitanya6416/event-collect-and-deliver/tree/main/src/backups)

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



