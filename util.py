from manim_rubikscube import *

# https://ruwix.com/blog/feliks-zemdegs-rubiks-world-record-2016-4-73/
FELIKS_SCRAMBLE_MOVES = [
    "U2",
    "F",
    "L2",
    "U2",
    "R2",
    "F",
    "L2",
    "F2",
    "L'",
    "D'",
    "B2",
    "R",
    "D2",
    "R'",
    "B'",
    "U'",
    "L'",
    "B'",
]


def invert_move(move):
    face, n_turns = parse_move(move)
    # Note these are already inverted
    endings = {
        1: "'",
        2: "2",
        3: "",
    }
    return face + endings[(n_turns + 4) % 4]


FELIKS_UNSCRAMBLE_MOVES = [invert_move(move) for move in FELIKS_SCRAMBLE_MOVES[::-1]]


def scramble_to_feliks(cube: RubiksCube):
    for move in FELIKS_SCRAMBLE_MOVES:
        cube.do_move(move)
