import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'client')))

import json
import time
from network import NetworkClient

class TestClient:
    def __init__(self):
        self.client = NetworkClient()
        self.player_id = None
        self.game_started = False

        self.client.on_message(self.handle_message)

        # Keep the test client running
        while True:
            time.sleep(1)

    def handle_message(self, data):
        print("[CLIENT] Received:", json.dumps(data, indent=2))

        if data.get("type") == "assign_id":
            self.player_id = data["player_id"]
            print(f"[CLIENT] Assigned ID: {self.player_id}")

        elif data.get("type") == "game_start" and not self.game_started:
            self.game_started = True
            print("[CLIENT] Game started — preparing move")
            time.sleep(2)

            base_positions = {
                1: (50, 400),
                2: (200, 400),
                3: (350, 400)
            }
            bx, by = base_positions[self.player_id]

            # Step 1: Drag to claim the gem
            drag_msg = {
                "player_id": self.player_id,
                "action": {
                    "type": "drag",
                    "gem_id": self.player_id - 1
                }
            }
            self.client.send(drag_msg)

            # Step 2: Move the gem to the base
            time.sleep(0.5)
            move_msg = {
                "player_id": self.player_id,
                "action": {
                    "type": "move",
                    "gem_id": 1,
                    "position": [bx + 50, by + 50]
                }
            }
            print(f"[CLIENT] Sending move: {move_msg}")
            self.client.send(move_msg)

if __name__ == "__main__":
    TestClient()
