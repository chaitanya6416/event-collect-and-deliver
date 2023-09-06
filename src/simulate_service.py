import random
import json
import time
from requests.models import Response


def deliver_and_get_response(port_number, payload):

    # Simulate random behavior
    response_delay = random.uniform(0, 5)  # Random delay in seconds

    response_code = random.choice([200, 200, 400, 400, 500])

    # let's always reject 5555.
    if int(port_number) == 5555:
        response_code = 400
        response_delay = 0

    # Simulate a delay
    time.sleep(response_delay)

    # Create a Response object
    response = Response()
    response.status_code = response_code

    if response_code == 200:
        response._content = json.dumps({
            'status': 200,
            'message': 'OK',
            'data': payload
        }).encode('utf-8')
    elif response_code == 400:
        response._content = json.dumps({
            'status': 400,
            'message': 'Bad Request',
            'error_details': 'Invalid payload'
        }).encode('utf-8')
    elif response_code == 500:
        response._content = json.dumps({
            'status': 500,
            'message': 'Internal Server Error',
            'error_details': 'Server encountered an error'
        }).encode('utf-8')
    else:
        response._content = json.dumps({
            'status': response_code,
            'message': 'Unknown Error'
        }).encode('utf-8')

    return response
