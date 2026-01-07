# Gem Grab

**Gem Grab** is a three-player competitive game where players race to drag and collect gems into their base before the round timer runs out. The player with the highest score at the end wins.

Group members:

Marcus Daudt 301460785

Sung Han 301475276

Nevin Seikhon 301562361

Minseo Kim 301608333

---

## Project Structure

```
client/
│   client.py       # Main client entry point with game loop and UI handling
│   network.py      # Handles client-side networking (connects to server)
│   ui.py           # Pygame-based user interface
│
server/
│   server.py       # Main server entry point, manages players and game loop
│   game.py         # Game logic: state updates, scoring, and object handling
│   client_test.py  # Testing client for development/debugging
│
shared/
│   constants.py    # Shared constants (server address/port, gem radius, etc.)
│   objects.py      # Dataclasses for shared objects (Gem, Player)
│   protocol.py     # Message encoding/decoding utilities (JSON over TCP)
│
README.md           # Project documentation (this file)
.gitignore          # Git ignore rules
```

---

## Requirements

- Python **3.12+**
- `pygame` (for client UI)
- Any other packages listed in `requirements.txt` or `environment.yml`

Install dependencies:

```bash
pip install pygame
```

---

## ▶ How to Run

### 1. Start the Server
In a terminal:
```bash
python server/server.py
```
The server will listen for connections from three clients.

### 2. Start Clients
In three separate terminals (or on three machines):
```bash
python client/client.py
```

Each client will connect to the server. Once all three clients click **Start Game**, the match begins.

---

## Networking Notes

- The default server address and port are set in `shared/constants.py`:
```python
SERVER_ADDRESS = "127.0.0.1"
SERVER_PORT = 12345
```
- For LAN or remote play, change `SERVER_ADDRESS` to the server machine’s IP.

---

## Game Flow

1. Server starts and waits for 3 clients to connect.
2. Clients click **Start Game** → enter loading screen.
3. When all 3 clients are connected, the server sends `game_start`.
4. Players drag gems into their base to score points.
5. Server broadcasts the current state every ~0.5 seconds.
6. When the timer ends, the server sends `game_end` with the winner.

---
