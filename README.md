# Event Collection and Delivery Service

The Event Collection and Delivery Service is a FastAPI-based application that collects event payloads and delivers them to destinations (for the simplicity of implementation, the destinations here in the project are just the local machine HTTP ports). This README provides an overview of the project design, structure & endpoints.

## Design

<img src="https://github.com/chaitanya6416/event-collect-and-deliver/assets/36512605/6df0f01c-b5e0-4c7d-a2d1-c72d5ab3c4cb" alt="collect-deliver" width="75%" height="75%">



The Event Collection and Delivery Service is designed to collect event payloads and deliver them to specified ports using threads. The application utilizes FastAPI for creating RESTful APIs, Redis for storing and managing payload data, and threading for parallel processing of payload delivery.


## API Endpoints

- `/collect_api`: POST endpoint for collecting event payloads. Requires `user_id` and `payload` fields in the JSON payload.
- `/start_delivery`: POST endpoint for starting payload delivery to a specified port.
- `/stop_delivery`: POST endpoint for stopping all payload delivery threads. Delivers the payload already in consideration and then exits. (this is different from SIGINT/ctrl+c signal. How SIGINT/ctrl+c is handled is mentioned below!).

## How to execute?

|Which module to run ?| command to run|
|---------------------|---------------|
|Run project| `docker-compose up` |
|Get coverage report | `make coverage` <br> Coverage(latest): 91%. <br> Screenshot for the same. <br> <img src="https://github.com/chaitanya6416/event-collect-and-deliver/assets/36512605/fb85f27f-0aa7-4032-905a-a491a3ef0fa1" alt="collect-deliver" width="75%" height="75%">|
|Get lint score | `make lint` |




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

- `delivery_thread.py`: Contains the `DeliveryThread` class responsible for delivering payloads to specified ports using threads.
- `global_threading_event.py`:  Declares & when used returns a single threading.event(), which is listened to by all threads to exit in case of SIGINT.
- `logger.py`: Declares basic  logging format. Imported by others and is used. Also has a special format to print thread_id when called log_with_thread_id().
- `main.py`: The main entry point of the FastAPI application.
- `redis_client.py`: Returns a redis instance when asked for.
- `routes.py`: Defines the API routes using FastAPI, including the `/collect_api`, `/start_delivery`, and `/stop_delivery` endpoints.
- `simulate_service`: Should be considered as if it is some external destination. It randomly responds to our requests (Delays, accepts, rejects).


## Some interesting concepts/articles on the development way
|About| Link|
|----|-----|
|Tenacity retry module. <br> Used this module earlier, but had to explore the source code to really find out the way the exit in case of threadin.event(). used `sleep=sleep_using_event`| https://tenacity.readthedocs.io/en/latest/ |
|Tini. <br> It ensures that the default signal handlers work for the software you run in your Docker image. While trying to give a sigint interupt while running the application on docker found an issue with fastapi shutdown. Hence found & used this. |https://github.com/krallin/tini|
|FastAPI lifespan shutdown issue discussion. <br> Spent a lot of time understanding the problem in the code & finally found this. |https://github.com/tiangolo/fastapi/issues/5072|
|apscheduler - Advanced Python Scheduler| https://apscheduler.readthedocs.io/en/3.x/index.html |



## Let's talk Test cases

- `test_payload_collection.py`
  - `test_postive_collect_api`: hits the /collect endpoint with a payload & checks if the sequence_number is incremented & stored in Redis.
  - `test_negative_collect_api`: When/collect endpoint is hit with improper payload, the API should respond with a 400 error status.

- `test_payload_delivery.py`
  - `test_positive_post_the_payload`: When a thread is actively running & is waiting to deliver any arrived payloads at /collect_api endpoint, it immediately delivers the payload to the destination port. Here we are spawning a thread to deliver a payload to a port, then hitting the /collect_api with a payload & checking whether the running thread is able to make a post request. We mock the actual delivery and just check if the post request is called.
  - `test_negative_post_the_payload`: After exhausting the set number of attempts, the program must raise a requests.RequestException. Here we are not mocking the request post method & willingly trying to make the payload delivery fail and then trying to check if an exception is raised by asserting like self.assertRaises(RequestException)

- `test_spawn_thread.py`
  - `test_start_delivery_and_check_threads`: When /start_delivery endpoint is hit along with a port number parameter, a thread has to be spawned. We are testing if any new threads are created here once the endpoint is hit.
  - `test_start_delivery_and_check_redis`:  When /start_delivery endpoint is hit along with a port number parameter, a thread has to be spawned and it has to store its delivery status in the Redis cache. Here we are checking whether the Redis status for the thread is set.
  - `test_duplicate_start_delivery_and_check_threads`: when we try to spawn threads to the same destination multiple times. Only one thread should be spawned. Before spawning a thread, the system must check the Redis if any such thread to the same destination is already registered & should not spawn duplicate threads.
 
- `test_spawn_thread_on_system_restart.py`
  -  `test_spawn_already_registered_thread_on_restart`: Imagine a scenario where the system was already running and a few delivery threads were already in the run. When the system restarts, it has to resume these threads as well. This functionality is tested here.
 
- `test_failed_delivery.py`
  -  `test_failed_delivery_and_check_redis_status`: The system is not only tracking the last successfully delivered payload but also a list of failed payload IDs. This functionality is tested here, whether a failed delivery is updated in the Redis.

- `test_successful_delivery.py`
  -  `test_successful_delivery_and_check_redis_status`: After a payload is successfully delivered, its status must be updated in redis. This functionality is checked here.


