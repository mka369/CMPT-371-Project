## Draw UI elements
import pygame
##from shared.constants import GEM_RADIUS

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
BLUE = (100, 100, 255)

pygame.font.init()
FONT = pygame.font.SysFont('Arial', 28)

class Button:
    def __init__(self, text, pos, size):
        self.text = text
        self.rect = pygame.Rect(pos, size)
        self.color = GRAY
        self.text_surface = FONT.render(text, True, BLACK)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit( ## Place the text.
            self.text_surface,
            self.text_surface.get_rect(center=self.rect.center)
        )
    
    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

class GameUI:
    def __init__(self, screen):
        self.screen = screen
        self.state = "main"
        self.clock_start = None
        self.duration = 30
        self.winner_ids = []

        self.start_button = Button("Start Game", (280, 250), (200, 60))
        ## self.restart_button = Button("Restart", (250, 300), (150, 50))
        self.quit_button = Button("Quit", (320, 300), (150, 50))

        self.draw_main_screen()
    
    def draw_main_screen(self):
        self.screen.fill(WHITE)
        title = FONT.render("Welcome to Gem Grab!", True, BLACK)
        self.screen.blit(title, (270, 150))
        self.start_button.draw(self.screen)
        pygame.display.flip()
    
    def draw_loading_screen(self):
        self.screen.fill(WHITE)
        loading_msg = FONT.render("Loading...", True, BLACK)
        self.screen.blit(loading_msg, (300, 250))
        pygame.display.flip()

    def draw_game_screen(self, game_state, player_id):
        self.screen.fill(WHITE)

        ## Draw gems.
        for gem in game_state.get("gems", []):
            x, y = gem["position"]
            color = RED if gem["is_collected"] else BLUE
            pygame.draw.circle(self.screen, color, (x, y), 10) ########### GEM_RADIUS

        ## Draw player bases.
        for player in game_state.get("players", []):
            base_color = GREEN if player["id"] == player_id else GRAY
            x, y, w, h = player["base"]
            pygame.draw.rect(self.screen, base_color, (x, y, w, h))
            label = FONT.render(f"P{player['id']}: {player['score']}", True, BLACK)
            self.screen.blit(label, (x, y - 30))
        
        ## Draw clock.
        if self.clock_start:
            elapsed = int(pygame.time.get_ticks() / 1000 - self.clock_start)
            remaining = max(0, self.duration - elapsed)
            timer = FONT.render(f"Time left: {remaining}s", True, BLACK)
            self.screen.blit(timer, (20, 20))
        
        pygame.display.flip()

    def draw_end_screen(self):
        self.screen.fill(WHITE)
        winner_ids = self.winner_ids
        #print(self.winner_ids)
        if winner_ids:
            names = ", ".join([f"P{id}" for id in winner_ids])
            text = f"Winner: {names}!"
        else:
            text = "Game Over!"
        result = FONT.render(text, True, BLACK)
        self.screen.blit(result, (330, 200))
        ##self.quit_button.draw(self.screen)
        pygame.display.flip()
    
    def render(self, game_state = None, player_id = None):
        if self.state == "main":
            self.draw_main_screen()
        elif self.state == "loading":
            self.draw_loading_screen()
        elif self.state == "game":
            self.draw_game_screen(game_state, player_id)
        elif self.state == "end":
            self.draw_end_screen()

    def button_click(self, mouse_pos):
        if self.state == "main":
            if self.start_button.is_clicked(mouse_pos):
                self.state = "game"
                self.clock_start = pygame.time.get_ticks() / 1000
                return "start_game"
        
        elif self.state == "game":
            return "play_game"
        
        elif self.state == "end":
            '''
            if self.restart_button.is_clicked(mouse_pos):
                self.state = "game"
                self.clock_start = pygame.time.get_ticks() / 1000
                return "restart_game"
            
            if self.quit_button.is_clicked(mouse_pos):
                self.state = "main"
                return "quit_to_main"
            '''

        return None