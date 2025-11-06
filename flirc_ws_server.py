#!/usr/bin/env python3
import asyncio, json, evdev, websockets, sys, os

# --- Configuration ---
STATIC_PATH = "/dev/input/by-id/usb-flirc.tv_flirc_B657C57351503639304A2020FF0C171C-if01-event-kbd"
PORT = 9000
LONG_PRESS_THRESHOLD = 0.35   # seconds before sending _DOWN

# --- State Tracking ---
key_states = {}           # keycode → {"time": t, "mods": [...]}
long_press_active = {}    # full_key → bool
active_modifiers = set()  # currently held modifiers
connected_clients = set() # WebSocket clients

# --- Modifier Mapping ---
MODIFIER_MAP = {
    "KEY_LEFTSHIFT": "LeftShift", "KEY_RIGHTSHIFT": "RightShift",
    "KEY_LEFTCTRL": "LeftCtrl",   "KEY_RIGHTCTRL": "RightCtrl",
    "KEY_LEFTALT": "LeftAlt",     "KEY_RIGHTALT": "RightAlt"
}

def find_flirc_device():
    """Locate the FLIRC input device."""
    if os.path.exists(STATIC_PATH):
        return STATIC_PATH
    for path in evdev.list_devices():
        dev = evdev.InputDevice(path)
        if "flirc" in dev.name.lower():
            print(f"✅ Auto-detected FLIRC at {path}", file=sys.stderr)
            return path
    raise FileNotFoundError("❌ FLIRC device not found!")

def is_modifier(k): return k in MODIFIER_MAP

async def broadcast_key(full_key):
    """Send key event JSON to all connected clients."""
    if not connected_clients:
        return
    message = json.dumps({"key": full_key})
    for ws in list(connected_clients):
        try:
            await ws.send(message)
        except Exception:
            connected_clients.discard(ws)
    print("➡️", {"key": full_key}, file=sys.stderr)

async def handle_key_event(key_event, event):
    """Process individual key events from evdev."""
    keycode, value, now = key_event.keycode, key_event.keystate, event.timestamp()

    # --- Modifier tracking ---
    if is_modifier(keycode):
        name = MODIFIER_MAP[keycode]
        if value == 1:
            active_modifiers.add(name)
        elif value == 0:
            active_modifiers.discard(name)
        return

    # Build current modifier+key combination
    current_mods = sorted(active_modifiers)
    full_key = "+".join(current_mods) + f"+{keycode}" if current_mods else keycode

    # --- Key press (value == 1) ---
    if value == 1:
        key_states[keycode] = {"time": now, "mods": current_mods}
        long_press_active[full_key] = False

    # --- Key hold / repeat (value == 2) ---
    elif value == 2:
        # Only applies for keys that emit repeats (like KEY_3/KEY_4)
        key_info = key_states.get(keycode)
        if not key_info:
            return
        # For held keys, don't rebuild modifiers — use the base keycode
        hold_key = keycode
        if not long_press_active.get(hold_key, False):
            if now - key_info["time"] >= LONG_PRESS_THRESHOLD:
                await broadcast_key(hold_key + "_DOWN")
                long_press_active[hold_key] = True

    # --- Key release (value == 0) ---
    elif value == 0:
        # When key releases, determine if it had a long press
        key_info = key_states.pop(keycode, None)
        if not key_info:
            return

        # Use base keycode (not modifier-based)
        release_key = keycode

        # If this was a long-press type key (KEY_3, KEY_4, KEY_1, KEY_2)
        if long_press_active.pop(release_key, False):
            await broadcast_key(release_key + "_UP")

        # Otherwise send normal press for short events (e.g., LeftShift+KEY_M/N)
        else:
            # Rebuild full key with modifiers at press time
            mods = key_info["mods"]
            full_key = "+".join(mods) + f"+{keycode}" if mods else keycode
            await broadcast_key(full_key)

async def flirc_reader():
    """Read events from the FLIRC device."""
    path = find_flirc_device()
    dev = evdev.InputDevice(path)
    print(f"🎧 Listening to {dev.name} on {path}", file=sys.stderr)
    async for ev in dev.async_read_loop():
        if ev.type == evdev.ecodes.EV_KEY:
            ke = evdev.categorize(ev)
            await handle_key_event(ke, ev)

async def ws_handler(ws):
    """Handle new WebSocket connections."""
    connected_clients.add(ws)
    print("🌐 Client connected", file=sys.stderr)
    try:
        await ws.wait_closed()
    finally:
        connected_clients.discard(ws)
        print("❌ Client disconnected", file=sys.stderr)

async def main():
    """Start WebSocket server and FLIRC reader."""
    print(f"🚀 WebSocket server on ws://0.0.0.0:{PORT}", file=sys.stderr)
    asyncio.create_task(flirc_reader())
    async with websockets.serve(ws_handler, "0.0.0.0", PORT):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Exiting cleanly.", file=sys.stderr)
