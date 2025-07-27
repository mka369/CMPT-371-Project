## Run the GUI and handle user input
import pygame
from ui import draw_main_screen, draw_game_screen, draw_end_screen
from network import NetworkClient
from shared.constants import GEM_RADIUS

def clicked(mouse_pos, gem):
    gx, gy = gem['position']
    mx, my = mouse_pos
    radius = GEM_RADIUS
    return (mx - gx) ** 2 + (my - gy) ** 2 <= radius ** 2

def handle_event(event):
    ## TODO: Handle button clicks, e.g., "Start", "Restart", "Back to Menu"

    if event.type == pygame.QUIT: ## User clicked the window's close button
        running = False
        ## TODO: If connected to server, tell the server I'm quitting.
    
    elif event.type == pygame.MOUSEBUTTONDOWN: ## User started dragging
        mouse_pos = pygame.mouse.get_pos()
        for gem in game_state['gems']:
            if clicked(mouse_pos, gem):
                dragging = True
                dragged_gem_id = gem['id']
                break
            
    elif event.type == pygame.MOUSEMOTION and dragging:
        ## TODO: Update the position change in real-time
        pass
            
    elif event.type == pygame.MOUSEBUTTONUP:
        if dragging:
            dragging = False
            drop_pos = pygame.mouse.get_pos()
            net.send({
                'player_id': 1, ## TODO: Read the ID properly
                'action': { 'type': "drag", 'gem_id': dragged_gem_id, 'final_pos': drop_pos }
            }) ## TODO: Send the action type, dragged gem's ID, and its final position.
            dragged_gem = None

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    net = NetworkClient()
    running = True
    dragging = False
    game_state = net.get_game_state()

    while running:
        for event in pygame.event.get(): ## Listen to user inputs.
            handle_event(event)
        
        net.listen()
        game_state = net.get_game_state()

        '''
        TODO: Take the correct field of game_state.

        if game_state == "main_menu":
            draw_main_screen(screen)
        elif game_state == "playing":
            draw_game_screen(screen, game_state)
        elif game_state == "game_over":
            draw_end_screen(screen, winner)
        '''

        pygame.display.flip()
        clock.tick(60) ## Limit the loop to run 60 times per second

    pygame.quit()

if __name__ == "__main__":
    main()
