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


FELIKS_ACTUAL_SOLUTION_MOVES_RAW = [
    "U'",
    "R",
    "F",
    "R'",
    "U'",
    "D",
    "L'",
    "U2",
    "L2",
    "U'",
    "L'",
    "U",
    "R'",
    "U",
    "R",
    "R'",
    "U",
    "R",
    "U",
    "R'",
    "U'",
    "R",
    "F",
    "R",
    "U'",
    "R'",
    "U'",
    "R",
    "U",
    "R'",
    "F'",
    "R",
    "U'",
    "R",
    "U",
    "R",
    "U",
    "R",
    "U'",
    "R'",
    "U'",
    "R2",
    "U",
]


def apply_feliks_turn(move):
    # Apply the INVERSE of x' y'. These are rotations of the whole cube,
    # so they essentially transform the moves performed
    replacements = {
        "U": "B",
        "D": "F",
        "L": "D",
        "R": "U",
        "F": "L",
        "B": "R",
    }
    return replacements[move[0]] + move[1:]


FELIKS_ACTUAL_SOLUTION_MOVES = [
    apply_feliks_turn(move) for move in FELIKS_ACTUAL_SOLUTION_MOVES_RAW
]
