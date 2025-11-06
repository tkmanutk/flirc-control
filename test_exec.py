#!/usr/bin/env python3
import time, json, sys

i = 0
while True:
    i += 1
    print(json.dumps({"count": i, "message": "Hello from Python!"}), flush=True)
    sys.stderr.write(f"debug: loop {i}\n")
    sys.stderr.flush()
    time.sleep(1)
