## Draw UI elements
import pygame

def draw_main_screen():
    ## Draw the main screen with buttons and background.
    screen.fill((0, 0, 0))

def draw_game_screen(game_state):
    ## Draw the game screen with the current game state.
    screen.fill((255, 255, 255))

def draw_end_screen(winner):
    ## Draw the end screen showing the winner.
    screen.fill((0, 0, 50))