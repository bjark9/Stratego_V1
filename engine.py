from typing import Tuple
import json
import pygame
import random
from game_state import place_blue, place_red, water, piece_rank


# If action is true, update the side
def update_side(action: bool, side: str) -> tuple[str, bool]:
    """
    Updates the side
    :param action: Boolean that tells if action is ongoing
    :param side: Side of the current move (blue/red)
    :return: Tuple
    """
    if action:
        if side == "blue":
            side = "red"
        else:
            side = "blue"
    action = False
    return side, action


# Return (piece_name, index) if a piece is found at position 'pos', else returns None,None
def get_piece_at_position(pos: tuple[int, int], side: str) -> tuple:
    """
    Return (piece_name, index) if a piece is found at position 'pos'.
    If none is found return None,None
    :param pos: Position of the mouse-click
    :param side: Side of the current move (blue/red)
    :type pos: Tuple
    :type side: str
    :return: (piece_name, index)
    :rtype: tuple[str, int]
    """
    if side == "blue":
        place = place_blue
    else:
        place = place_red
    for piece_name, values in place.items():
        for index, (x, y) in enumerate(values):
            if (x, y) == pos:
                return piece_name, index
    return None, None


# In this function we check if the piece can move and move them if possible
def move_piece(
    piece_name, index, start_position, new_pos, adj_cases, side
) -> tuple[bool, bool]:
    """
    Checks all the constraints for moving the piece.
    Returns a tuple with booleans to tell if piece can move and change the action flag if the piece moved.
    :param piece_name: Name of the piece
    :param index: Index of the
    :param start_position:
    :param new_pos:
    :param adj_cases: Adjacent cases with respect to start_position
    :param side: Side of the current move (blue/red)
    :return: tuple of booleans: first one to tell if the piece can move, second one to change action flag
    """
    # We break the movement of the piece if can_move returns False
    if not can_move(piece_name):
        return False, False
    if not valid_move(side, start_position, new_pos, adj_cases, piece_name):
        return False, False

    x, y = new_pos
    # Move the piece
    if side == "blue":
        place_blue[piece_name][index] = (x, y)
    if side == "red":
        place_red[piece_name][index] = (x, y)

    return True, True  # (moved_successfully, action_flag)


# Can the piece move (Bombs and Flags can't move)
def can_move(piece_name: str) -> bool:
    """
    Function that finds out if the piece itself can move.
    :param piece_name: Name of the selected piece
    :return: Boolean that indicates if piece can move
    """
    if piece_name == "Flag" or piece_name == "Bomb":
        return False
    return True


# Checks if the case where the pawn moves is an enemy
def is_enemy(side, pos) -> bool:
    """
    Checks if the case where the pawn moves is an enemy
    :param side: Side of the current move (blue/red)
    :param pos: Position
    :return: Boolean, True -> enemy. False -> not an enemy
    """
    if side == "blue":
        place = place_red
    else:
        place = place_blue
    for values in place.values():
        for index, (x, y) in enumerate(values):
            if (x, y) == pos:
                return True
    return False


# Get positions of cases nsew of the current case
# Returns list of coördinates
def get_adjacent_cases(side: str, pos: tuple) -> list:
    """
    Get position of the current case and returns a list of the coordinates of its adjacent cases
    :param side: Side of the current action (blue/red)
    :param pos: Position of the case from which we want the adjacent cases
    :return: List of adjacent cases
    """
    adjacent_cases = []

    # Get the name and index of the piece where you clicked
    name, index = get_piece_at_position(pos, side)

    if side == "blue":
        place = place_blue
    else:
        place = place_red

    # Create the rectangles adjacent to the selected piece, create a surface? -> easier if set of coords
    for piece_name, values in place.items():
        if piece_name == name:
            for idx, (x, y) in enumerate(values):
                if index == idx:
                    north = (x - 80, y)
                    east = (x, y + 80)
                    south = (x + 80, y)
                    west = (x, y - 80)
                    adjacent_cases.append(north)
                    adjacent_cases.append(east)
                    adjacent_cases.append(south)
                    adjacent_cases.append(west)
                    # Remove cases that are out of the board
                    if x - 80 < 0:
                        adjacent_cases.remove(north)
                    if y - 80 < 0:
                        adjacent_cases.remove(west)
                    if x + 80 > 720:
                        adjacent_cases.remove(south)
                    if y + 80 > 720:
                        adjacent_cases.remove(east)
                    return adjacent_cases


# Checks if the move is valid
def valid_move(
    side: str,
    start_position: Tuple,
    end_position: tuple[int, int],
    adj_cases: list,
    piece_name,
) -> bool:
    """
    Checks if the move is valid
    :param side: Side of the current action (blue/red)
    :param start_position: Start position of the move (assigned to first mousebutton1 click)
    :param end_position: End position of the move (assigned to second mousebutton1 click)
    :param adj_cases: Adjacent cases of the case of the start position
    :param piece_name: Name of the piece
    :return: Boolean that tells us if the move is valid or not
    """
    occupant = is_occupied(end_position)
    # print(occupant)

    if not can_move(piece_name):
        return False

    # Block water
    if occupant == "water":
        # print("Cannot move into water")
        return False

    # Block friendly fire
    if occupant == side:
        # print("Cannot move onto own piece")
        return False

    if piece_name == "Scout":
        return scout_movement(side, start_position, end_position)
    else:
        # Check if end_position is in the adjacent cases:
        for coords in adj_cases:
            if coords == end_position:
                return True
    return False


# Can move multiple cases, but can't jump over occupied cases
def scout_movement(side: str, start_pos: tuple, end_pos: tuple) -> bool:
    """
    Checks if the movement of the scout is valid.
    Scout can't move diagonally and can't jump over pieces.
    :param side: Side of the current action (red/blue)
    :param start_pos: Starting position of the scout
    :param end_pos: End position of the scout
    :return: Boolean
    """
    # List of possible cases scout can move to
    list_possible_rect = []
    x1, y1 = start_pos

    for i in range(1, 9):  # start at 1 to exclude the current square
        step = i * 80
        list_possible_rect.append(pygame.Rect(x1 + step, y1, 80, 80))  # right
        list_possible_rect.append(pygame.Rect(x1 - step, y1, 80, 80))  # left
        list_possible_rect.append(pygame.Rect(x1, y1 + step, 80, 80))  # down
        list_possible_rect.append(pygame.Rect(x1, y1 - step, 80, 80))  # up

    x2, y2 = end_pos

    # If the end position doesn't collide with rectangles in list of possible rectangles -> False
    if not any(rectangle.collidepoint(x2, y2) for rectangle in list_possible_rect):
        # print("Can't move diagonally")
        return False

    # If out of board
    if x2 > 720 or y2 > 720:
        print("Out of bounds")
        return False

    # The distance in number of cases (can be negative)
    dx = (x2 - x1) // 80
    dy = (y2 - y1) // 80

    # See if the scout makes a step in either direction
    steps = max(abs(dx), abs(dy))
    if steps == 0:
        return False  # No movement

    if dx == 0:
        step_x = 0
    else:
        step_x = dx // abs(dx)
    if dy == 0:
        step_y = 0
    else:
        step_y = dy // abs(dy)
    # We check if there are other pieces in its track
    for i in range(1, int(steps)):
        xi = x1 + i * step_x * 80
        yi = y1 + i * step_y * 80
        if is_occupied((xi, yi)):
            # print("Not the first piece in its track")
            return False

    target = is_occupied(end_pos)
    if target == "water" or target == side:
        # print("Can't land on water or own piece")
        return False

    # print("Valid move for scout")
    return True


# Checks if the case is occupied, and checks if it's an enemy/ally/water/empty
def is_occupied(pos: tuple[int, int]) -> str | None:
    """
    Checks if the case is occupied, and returns if it's red/blue/water/None
    :param pos: Position of the case we want to check
    :returns red/blue/water/None
    """
    for wat in water:
        if wat.collidepoint(pos):
            return "water"
    for positions in place_red.values():
        for x, y in positions:
            if pygame.Rect(x, y, 80, 80).collidepoint(pos):
                return "red"
    for positions in place_blue.values():
        for x, y in positions:
            if pygame.Rect(x, y, 80, 80).collidepoint(pos):
                return "blue"
    return None


# Will check which one is the winner and delete the loser. Will also move the winner to the losers place
def winner_of_combat(pos1, pos2, side) -> tuple[bool, bool]:
    """
    Checks which one is the winner of the combat and deletes the loser
    :param pos1: Position of the attacker
    :param pos2: Position of the defender
    :param side: Side of the current action
    :return: tuple of booleans, one to change the action to True
    """
    attacker_name, attacker_index = get_piece_at_position(pos1, side)
    # Change side after getting the attacker
    if side == "blue":
        opponent_side = "red"
    else:
        opponent_side = "blue"
    defender_name, defender_index = get_piece_at_position(pos2, opponent_side)
    attacker_rank = piece_rank.get(attacker_name)
    defender_rank = piece_rank.get(defender_name)

    if attacker_rank is None or defender_rank is None:
        print("Combat error: unknown piece rank.")
        return False, False

    # Win the game
    if defender_name == "Flag":
        return True, True

    # Miner -> bomb interaction
    if attacker_name == "Miner" and defender_name == "Bomb":
        print("Miner defeats the bomb")
        if opponent_side == "red":
            del place_red[defender_name][defender_index]
        else:
            del place_blue[defender_name][defender_index]

        # Move attacker to defender's position
        if side == "blue":
            place_blue[attacker_name][attacker_index] = pos2
        else:
            place_red[attacker_name][attacker_index] = pos2

    # Spy -> Marshall
    elif attacker_name == "Spy" and defender_name == "Marshall":
        print("Spy attacks and defeats the Marshall")
        if opponent_side == "red":
            del place_red[defender_name][defender_index]
        else:
            del place_blue[defender_name][defender_index]

        # Move attacker to defender's position
        if side == "blue":
            place_blue[attacker_name][attacker_index] = pos2
        else:
            place_red[attacker_name][attacker_index] = pos2

    # Attacker wins
    elif attacker_rank < defender_rank:
        print("Attacker wins!")
        # Remove defender
        if opponent_side == "red":
            del place_red[defender_name][defender_index]
        else:
            del place_blue[defender_name][defender_index]

        # Move attacker to defender's position
        if side == "blue":
            place_blue[attacker_name][attacker_index] = pos2
        else:
            place_red[attacker_name][attacker_index] = pos2

    # Defender wins
    elif attacker_rank > defender_rank:
        print("Defender wins")
        # Remove attacker
        if side == "blue":
            del place_blue[attacker_name][attacker_index]
        else:
            del place_red[attacker_name][attacker_index]

        # Defender stays in place

    # Draw: both die
    else:
        print("Draw. Both pieces die.")
        if side == "blue":
            del place_blue[attacker_name][attacker_index]
            del place_red[defender_name][defender_index]
        else:
            del place_red[attacker_name][attacker_index]
            del place_blue[defender_name][defender_index]
    # action = True
    return False, True


# After a move, send the move to the game_history.txt file
def send_to_history(piece_name, start_position, end_position, side):
    """
    Send the move to the history.txt file
    :param piece_name: Name of the piece
    :param start_position: Starting position of the piece
    :param end_position: End position of the piece
    :param side: Side of the current action
    :return: None
    """
    with open("game_history.txt", "a") as file:
        side = side.capitalize()
        file.write(
            f"{side} {piece_name} moved from {start_position} to {end_position}  \n"
        )


# We will call this function when the "save" button is clicked
def save_game():
    # Prepare data to serialize
    game_data = {
        "blue_pieces": place_blue,
        "red_pieces": place_red,
    }

    # Write to JSON
    with open("sample.json", "w") as outfile:
        json.dump(game_data, outfile, indent=4)  # Indent for readability


# Load the game
def load_game():
    with open("sample.json", "r") as file:
        data = json.load(file)
    # print(data)
    red_pieces = data["red_pieces"]
    blue_pieces = data["blue_pieces"]
    print(red_pieces)
    return red_pieces, blue_pieces


# ------------------------------------------------- IA -----------------------------------------------------------------
# Get random piece that can move
def get_random_piece():
    candidates = []
    # fill candidates with pieces that can move and their respective position
    for piece_name, positions in place_red.items():
        for index, pos in enumerate(positions):
            adj_cases = get_adjacent_cases("red", pos)
            for case in adj_cases:
                if valid_move("red", pos, case, adj_cases, piece_name):
                    candidates.append((piece_name, pos, index))
    # Take a random from the list candidates
    random_piece = random.choice(candidates)
    # print(random_piece)
    return random_piece


# Don't move yet, just prepare the movement
def random_move_piece_ia():
    piece_name, pos, index = get_random_piece()
    print(place_red[piece_name])
    # Get the possible moves
    possible_moves = []
    adj_cases = get_adjacent_cases("red", pos)
    for case in adj_cases:
        if valid_move("red", pos, case, adj_cases, piece_name):
            possible_moves.append(case)
    # print(possible_moves)
    move = random.choice(possible_moves)
    # print(f"start: {pos}, end: {move}")
    # Move the piece on one of the possible moves randomly
    return piece_name, pos, move, index
