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
            Gem(id=9, position=(620, 250)),
            Gem(id=10, position=(130, 180)),
            Gem(id=11, position=(170, 250)),
            Gem(id=12, position=(240, 120)),
            Gem(id=13, position=(280, 260)),
            Gem(id=14, position=(340, 140)),
            Gem(id=15, position=(370, 240)),
            Gem(id=16, position=(430, 120)),
            Gem(id=17, position=(520, 140)),
            Gem(id=18, position=(560, 240)),
            Gem(id=19, position=(610, 150)),
            Gem(id=20, position=(150, 130)),
            Gem(id=21, position=(220, 180)),
            Gem(id=22, position=(260, 230)),
            Gem(id=23, position=(320, 170)),
            Gem(id=24, position=(360, 280)),
            Gem(id=25, position=(400, 170)),
            Gem(id=26, position=(450, 260)),
            Gem(id=27, position=(500, 200)),
            Gem(id=28, position=(570, 270)),
            Gem(id=29, position=(620, 200)),
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

        winners = []
        highscore = max(player.score for player in self.players)
        for player in self.players:
            if player.score == highscore:
                winners.append(player.id)
    
        end_msg = encode_message({
            "type": "game_end",
            "winner": winners,
            "score": highscore
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

            if action["type"] == "quit": ## Player quit the game.
                for player in self.players:
                    if player.id == player_id:
                        player.has_quit = True
                        print(f"[GAME] Player {player_id} quit the game.")
                        break
                return

            if action["type"] == "drag": ## Player dragging a gem.
                print(f"[GAME] Player {player_id} dragging gem {action['gem_id']}")
                for gem in self.gems:
                    if gem.id == action["gem_id"] and gem.owner_id is None:
                        gem.owner_id = player_id ## Lock the gem to the player.
                        break

            elif action["type"] == "move": ## Player moving a gem.
                print(f"[GAME] Player {player_id} moving gem {action['gem_id']} to {action['position']}")
                for gem in self.gems:
                    if gem.id == action["gem_id"] and gem.owner_id == player_id and not gem.is_collected:
                        gem.position = tuple(action["position"]) ## Update gem position.
                        
                        for player in self.players: ## Check if the gem is dropped in a player's base.
                            if player.id == player_id:
                                px, py, pw, ph = player.base
                                gx, gy = gem.position
                                if px <= gx <= px + pw and py <= gy <= py + ph:
                                    gem.is_collected = True
                                    player.score += 1
                                    break

            elif action["type"] == "drop": ## Player dropping a gem.
                print(f"[GAME] Player {player_id} dropping gem {action['gem_id']} at {action['drop_pos']}")
                for gem in self.gems:
                    if gem.id == action["gem_id"] and gem.owner_id == player_id and not gem.is_collected:
                        gem.position = tuple(action["drop_pos"])
                        
                        for player in self.players: ## Check if the gem is dropped in a player's base.
                            px, py, pw, ph = player.base
                            gx, gy = gem.position
                            if px <= gx <= px + pw and py <= gy <= py + ph:
                                gem.is_collected = True
                                player.score += 1
                                break

                        ## Unlock gem if not dropped in a base.
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
