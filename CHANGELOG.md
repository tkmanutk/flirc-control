# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2025-11-06

This is the initial stable release of the Flirc WebSocket Server.

### Features

- **Device Auto-Detection:** Automatically finds the Flirc USB device, falling back to a static path if needed.
- **WebSocket Server:** Broadcasts key events to all connected clients (e.g., Node-RED) over a WebSocket connection on port 9000.
- **Advanced Key Event Logic:**
    - Distinguishes between short presses and long presses (e.g., `KEY_UP` vs. `KEY_UP_DOWN`/`KEY_UP_UP`).
    - Correctly handles modifier keys (Shift, Ctrl, Alt) to create combination key events (e.g., `LeftShift+KEY_M`).
- **Robust Connection Handling:** Gracefully adds and removes clients as they connect and disconnect.
- **Daemonized Operation:** Designed to run continuously as a background service.
- **Configuration:** Key parameters like port and long-press threshold are easily configurable at the top of the script.


