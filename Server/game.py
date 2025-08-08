## Handle game logic (mutex synchronization)
from shared.objects import Gem, Player
from shared.protocol import encode_message
import threading
import time

class Game:
    def __init__(self):
        ## Initialize the game with players and gems.
        self.players = [
            Player(id=1, name="Player1", base=(50, 400, 100, 100)),
            Player(id=2, name="Player2", base=(300, 400, 100, 100)),
            Player(id=3, name="Player3", base=(550, 400, 100, 100))
        ]

        self.gems = [
            Gem(id=0, position=(100, 100)),
            Gem(id=1, position=(200, 150)),
            Gem(id=2, position=(300, 200)),
            Gem(id=3, position=(480, 180)),
            Gem(id=4, position=(410, 210)),
            Gem(id=5, position=(600, 300)),
            Gem(id=6, position=(550, 110)),
            Gem(id=7, position=(580, 200)),
            Gem(id=8, position=(460, 150)),
            Gem(id=9, position=(620, 250))
            ]
        self.game_over = False
        self.game_lock = threading.Lock()

    def start(self, clients):
        ## Start the game loop.
        print("[GAME] Game started.")
        start_msg = encode_message({"type": "game_start"})
        for client in clients:
            try:
                client.sendall(start_msg)
            except:
                print(f"[GAME] Failed to send game_start to {client}")

        start_time = time.time()
        duration = 30

        while not self.game_over:
            time.sleep(0.5) ## Broadcast every 0.5s
            state = self.get_state()
            encoded = encode_message(state)
            for client in clients:
                try:
                    client.sendall(encoded)
                except:
                    print(f"[GAME] Failed to send state to {client}")

            if time.time() - start_time >= duration:
                self.game_over = True
                print("[GAME] Time's up. Game over.")

        winner = max(self.players, key=lambda p: p.score)
        end_msg = encode_message({
            "type": "game_end",
            "winner": winner.name,
            "score": winner.score
        })
        for client in clients:
            try:
                client.sendall(end_msg)
            except:
                print(f"[GAME] Failed to send game_end to {client}")

        time.sleep(5)

        for client in clients:
            try:
                client.close()
            except:
                print("[GAME] Failed to close client cleanly")


    def process_input(self, player_id, action):
        ## Process player input and update game state.
        with self.game_lock:
            action_type = action.get("type")

            if action["type"] == "quit":
                for player in self.players:
                    if player.id == player_id:
                        player.has_quit = True
                        print(f"[GAME] Player {player_id} quit the game.")
                        break
                return

            if action["type"] == "drag":
                print(f"[GAME] Player {player_id} dragging gem {action['gem_id']}")
                for gem in self.gems:
                    if gem.id == action["gem_id"] and gem.owner_id is None:
                        gem.owner_id = player_id
                        break

            elif action["type"] == "move":
                print(f"[GAME] Player {player_id} moving gem {action['gem_id']} to {action['position']}")
                for gem in self.gems:
                    if gem.id == action["gem_id"] and gem.owner_id == player_id and not gem.is_collected:
                        gem.position = tuple(action["position"])       
                        
                        for player in self.players:
                            if player.id == player_id:
                                px, py, pw, ph = player.base
                                gx, gy = gem.position
                                if px <= gx <= px + pw and py <= gy <= py + ph:
                                    gem.is_collected = True
                                    player.score += 1
                                    break

            elif action["type"] == "drop":
                print(f"[GAME] Player {player_id} dropping gem {action['gem_id']} at {action['drop_pos']}")
                for gem in self.gems:
                    if gem.id == action["gem_id"] and gem.owner_id == player_id and not gem.is_collected:
                        gem.position = tuple(action["drop_pos"])
                        
                        for player in self.players: ## Allow player to drop gems in other players' bases.
                            px, py, pw, ph = player.base
                            gx, gy = gem.position
                            if px <= gx <= px + pw and py <= gy <= py + ph:
                                gem.is_collected = True
                                player.score += 1
                                break

                        ## Reset gem if not dropped in a base.
                        if not gem.is_collected:
                            gem.owner_id = None
                            break
    
    def get_state(self):
        ## Get the current game state.
        with self.game_lock:
            return {
                'type': "state_update",
                'players': [player.to_dict() for player in self.players],
                'gems': [gem.to_dict() for gem in self.gems],
                'game_over': self.game_over
            }
