import pygame
import pytest
import game_state

from engine import (
    update_side,
    get_piece_at_position,
    can_move,
    is_enemy,
    get_adjacent_cases,
    valid_move,
    scout_movement,
    is_occupied,
    winner_of_combat,
    move_piece,
    send_to_history,
    action,
    side,
)

# When we start with side == "blue" this function should return "red".
# After calling the function action needs to be set to False
def test_red_update_side(monkeypatch):
    # Whatever the values of side and action were, we override them for this test
    monkeypatch.setattr("engine.action", True) # Action is temporarily set to True
    monkeypatch.setattr("engine.side", "blue") # Side is temporarily set to blue
    new_side = update_side()
    assert new_side == "red"
    assert action is False

# When we start with side == "red" this function should return "blue"
def test_blue_update_side(monkeypatch):
    monkeypatch.setattr("engine.action", True)  # Action is temporarily set to True
    monkeypatch.setattr("engine.side", "red")  # Side is temporarily set to blue
    new_side = update_side()
    assert new_side == "blue"
    assert action is False