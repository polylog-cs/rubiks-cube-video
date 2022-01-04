import glob
import random

from manim_rubikscube import *
from manim import ThreeDScene, smooth

from manim_rubikscube import cube_utils


class RubikScene(ThreeDScene):
    def __init__(self, *args, **kwargs):
        super(RubikScene, self).__init__(*args, **kwargs)
        self.camera.set_focal_distance(20000.0)
        self.camera.should_apply_shading = False
        self.bfs_counter = 0
        self.cube_sounds = []

    def play_bfs_sound(self, time_offset=0, animation_run_time=None):
        if animation_run_time is not None:
            assert (
                time_offset == 0
            ), "Nelze nastavit jak time_offset tak animation_length"
            time_offset = max(
                0, min(animation_run_time - 0.2, animation_run_time * 0.5)
            )

        self.add_sound(f"audio/bfs/bfs_{self.bfs_counter:03d}", time_offset=time_offset)
        self.bfs_counter += 1
    
    def play_cube_sound(self, time_offset=0, animation_run_time=None):
        if animation_run_time is not None:
            assert (
                time_offset == 0
            ), "Nelze nastavit jak time_offset tak animation_length"
            time_offset = max(
                0, min(animation_run_time - 0.2, animation_run_time * 0.5)
            )

        if not self.cube_sounds:
            self.cube_sounds = glob.glob("audio/cube/r*.wav")
            random.shuffle(self.cube_sounds)

        self.add_sound(self.cube_sounds.pop(), time_offset=time_offset)


def bfs(adj, start):
    res_vertices = [[start]]
    res_edges = [[]]
    seen = set([start])

    while True:
        cur_vertices = []
        cur_edges = []

        for v1 in res_vertices[-1]:
            for v2 in adj[v1]:
                cur_edges.append((v1, v2))

                if v2 not in seen:
                    cur_vertices.append(v2)
                    seen.add(v2)

        if cur_vertices:
            res_vertices.append(cur_vertices)
            res_edges.append(cur_edges)
        else:
            res_edges.append(cur_edges)
            break

    return res_vertices, res_edges


# https://ruwix.com/blog/feliks-zemdegs-rubiks-world-record-2016-4-73/
# TODO check (with our program?) this is indeed the best solution
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

POSSIBLE_MOVES = [
    "U",
    "U'",
    "U2",
    "D",
    "D'",
    "D2",
    "L",
    "L'",
    "L2",
    "R",
    "R'",
    "R2",
    "F",
    "F'",
    "F2",
    "B",
    "B'",
    "B2",
]
POSSIBLE_MOVES = [
    "U",
    "D",
    "L",
    "R",
    "F",
    "B",
    "U2",
    "D2",
    "L2",
    "R2",
    "F2",
    "B2",
    "U'",
    "D'",
    "L'",
    "R'",
    "F'",
    "B'",
]
