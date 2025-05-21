from typing import Tuple

import pygame
from game_state import place_blue, place_red

# TODO : maybe create a which_side function to not repeat the if...else to get to know the side

# update_side
action = False
side = "blue"


def update_side():
    global action, side
    if action:
        if side == "blue":
            side = "red"
        else:
            side = "blue"
    action = False
    return side


def get_piece_at_position(pos, side) -> str:
    """
    Return (piece_name, index) if a piece is found at position 'pos'
    :param pos: Position of the mouse-click
    :type pos: Tuple
    :return: piece_name, index
    :rtype: str, int
    """
    if side == "blue":
        place = place_blue
    else:
        place = place_red
    for piece_name, values in place.items():
        for index, (x, y) in enumerate(values):
            piece_rect = pygame.Rect(x, y, 80, 80)
            if piece_rect.collidepoint(pos):
                return piece_name, index
    return None, None


# Update position after move
# In this function we change the flag action to True so that update_side gets called
def move_piece(piece_name, index, new_pos):
    global action
    # We break the movement of the piece if can_move returns False
    if not can_move(piece_name):
        return False

    x, y = new_pos
    if side == "blue":
        place_blue[piece_name][index] = (x, y)
    if side == "red":
        place_red[piece_name][index] = (x, y)

    print(f"{piece_name} à bougé")
    action = True


# Can the piece move (Bombs and Flags can't move)
def can_move(piece_name: str) -> bool:
    if piece_name == "Flag" or piece_name == "Bomb":
        return False
    return True


# Checks if the case where the pawn moves is a enemy
def is_enemy(side, pos):
    if side == "blue":
        place = place_red
    else:
        place = place_blue
    for values in place.values():
        for index, (x, y) in enumerate(values):
            piece_rect = pygame.Rect(x, y, 80, 80)
            if piece_rect.collidepoint(pos):
                print("Ceci est un ennemi")


# Can the piece move on this place
def valid_move(piece_name: str, side: str, start_position: Tuple, end_position: Tuple):
    # The end_position is not empty
    if not is_empty(end_position):
        return False
    if side == "blue":
        place = place_blue
    else:
        place = place_red


def is_empty(pos):
    for values in place_red.values():
        for index, (x, y) in enumerate(values):
            case = pygame.Rect(x, y, 80, 80)
            if case.collidepoint(pos):
                return False
    for values in place_blue.values():
        for index, (x, y) in enumerate(values):
            case = pygame.Rect(x, y, 80, 80)
            if case.collidepoint(pos):
                return False
    print("Is empty")
    return True


def remove_pawn_after_move(): ...


def do_win(piece): ...
