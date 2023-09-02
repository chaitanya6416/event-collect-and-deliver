''' This code opens up a port to listen and is used to test the delivery of payloads '''

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import random
import time


class RequestHandler(BaseHTTPRequestHandler):
    ''' each incomming request has to accepted or rejected.
        If accepted, should accept with a random delay.
        Then response has to be sent back.
        All this is implemented here'''
    def _send_response(self, status_code, message):
        ''' to respond after accepting '''
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        response = {"message": message}
        self.wfile.write(json.dumps(response).encode("utf-8"))

    def do_post(self):
        ''' recieved payload '''
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length).decode("utf-8")
        payload = json.loads(post_data)

        print("*" * 100)
        print("Received POST request:")
        print("User ID:", payload.get("user_id"))
        print("Payload:")
        print("-" * 40)
        print(json.dumps(payload, indent=2))
        print("-" * 40)
        print("Sequence Number:", payload.get("sequence_number"))

        # Introduce random payload rejection
        if random.random() < 0.3:  # Adjust the probability as needed
            print("Payload rejected.")
            self._send_response(400, "Payload rejected")
            return

        # Introduce delay in payload acceptance
        # Random delay between 0.5 and 2.0 seconds
        delay = random.uniform(0.5, 2.0)
        print(f"Delaying payload acceptance by {delay:.2f} seconds...")
        time.sleep(delay)

        self._send_response(200, "Request received successfully")
        print("*" * 100)


def run_server(port):
    ''' start server to listen on input port '''
    server_address = ("", port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"Starting server on port {port}...")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()
        print("Server stopped.")


if __name__ == "__main__":
    input_port = int(input("Enter port number: "))
    run_server(input_port)
