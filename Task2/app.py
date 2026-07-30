from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import socket
import threading
import time
import random

from prometheus_client import Counter, CONTENT_TYPE_LATEST, generate_latest


POD_NAME = os.getenv("POD_NAME") or os.getenv("HOSTNAME") or "unknown-pod"
POD_NAMESPACE = os.getenv("POD_NAMESPACE") or "default"

# Allocate some memory on each GET / to make memory usage respond to load.
# This allows us to test HPA based on memory utilization.
ALLOC_CHUNK_BYTES = int(os.getenv("ALLOC_CHUNK_BYTES", "262144"))  # 256KiB
ALLOC_WINDOW_SECONDS = int(os.getenv("ALLOC_WINDOW_SECONDS", "10"))  # keep allocations for last N seconds


http_requests_total = Counter(
    "http_requests_total",
    "Total requests for GET /",
    ["pod", "namespace"],
)

# Cap retained chunks to avoid OOM before HPA reacts (limit 30Mi, target 80% = 24Mi).
MAX_ALLOC_CHUNKS = int(os.getenv("MAX_ALLOC_CHUNKS", "40"))
_allocations = []
_lock = threading.Lock()


def _gc_worker():
    while True:
        cutoff = time.time() - ALLOC_WINDOW_SECONDS
        with _lock:
            # Drop expired chunks
            while _allocations and _allocations[0][0] < cutoff:
                _allocations.pop(0)
        time.sleep(1)


threading.Thread(target=_gc_worker, daemon=True).start()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            http_requests_total.labels(pod=POD_NAME, namespace=POD_NAMESPACE).inc()

            # Allocate and keep for a short window to increase RSS under load.
            with _lock:
                chunk = bytearray(ALLOC_CHUNK_BYTES)
                # Touch pages so RSS actually grows (important for metrics-server).
                for i in range(0, len(chunk), 4096):
                    chunk[i] = 1
                _allocations.append((time.time(), chunk))
                if len(_allocations) > MAX_ALLOC_CHUNKS:
                    _allocations.pop(0)

            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"{POD_NAME}\n".encode("utf-8"))
            return

        if self.path == "/metrics":
            data = generate_latest()
            self.send_response(200)
            self.send_header("Content-Type", CONTENT_TYPE_LATEST)
            self.end_headers()
            self.wfile.write(data)
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        # Keep logs short to avoid huge outputs during tests.
        return


def main():
    port = int(os.getenv("PORT", "8080"))
    server = HTTPServer(("", port), Handler)
    print(f"Starting server on :{port} (pod={POD_NAME}, ns={POD_NAMESPACE})")
    server.serve_forever()


if __name__ == "__main__":
    main()

