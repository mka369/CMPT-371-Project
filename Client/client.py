## Run the GUI and handle user input
import pygame
from ui import draw_main_screen, draw_game_screen, draw_end_screen
from network import NetworkClient

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    client = NetworkClient()
    client.on_message(lambda data: print("[UI] Got:", data))


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

if __name__ == "__main__":
    main()
