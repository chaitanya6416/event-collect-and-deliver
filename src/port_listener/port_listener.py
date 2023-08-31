from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import random
import time

class RequestHandler(BaseHTTPRequestHandler):
    def _send_response(self, status_code, message):
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        response = {"message": message}
        self.wfile.write(json.dumps(response).encode("utf-8"))

    def do_POST(self):
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
        delay = random.uniform(0.5, 2.0)  # Random delay between 0.5 and 2.0 seconds
        print(f"Delaying payload acceptance by {delay:.2f} seconds...")
        time.sleep(delay)

        self._send_response(200, "Request received successfully")
        print("*" * 100)

def run_multiple_ports(ports):
    servers = []
    for port in ports:
        server_address = ("", port)
        httpd = HTTPServer(server_address, RequestHandler)
        servers.append(httpd)
        print(f"Starting server on port {port}...")
    print(servers)
    try:
        for server in servers:
            server.serve_forever()
    except KeyboardInterrupt:
        for server in servers:
            server.shutdown()
            print("Server stopped.")

if __name__ == "__main__":
    input_port = int(input("Enter port number: "))
    selected_ports = [input_port]
    run_multiple_ports(selected_ports)
