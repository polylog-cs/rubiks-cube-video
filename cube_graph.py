import itertools
from numpy.linalg import norm
import random
import math
from manim import *

# Use our fork of manim_rubikscube!
from manim_rubikscube import *

# This also replaces the default colors
from solarized import *

import util


cube.DEFAULT_CUBE_COLORS = [BASE3, RED, GREEN, YELLOW, ORANGE, BLUE]

# https://colorswall.com/palette/171
cube.DEFAULT_CUBE_COLORS = [
    "#ffffff",
    "#b71234",
    "#009b48",
    "#ffd500",
    "#ff5800",
    "#0046ad",
]

"""
what you see is just a tiny part of the neighborhood
of the solved cube. Remember, every cube has 18
neighbors in the full graph!
"""


class CubeGraph(util.RubikScene):  # MovingCameraScene):
    def construct(self):
        self.next_section(skip_animations=False)
        # self.camera.frame.save_state()

        solved = RubiksCube(cubie_size=0.3)

        nodes = [solved]
        edges = []
        can_be_outside = set()
        anims_to_do = []

        def new_cube(cube, move, shift, outside=False):
            c = cube.copy().do_move(move).shift(shift)
            nodes.append(c)
            edges.append((cube, c))
            if outside:
                can_be_outside.add(len(nodes) - 1)
            anims_to_do.append((cube, c, move))
            return c

        def add_edge(c1, c2, move):
            edges.append((c1, c2))
            anims_to_do.append((c1, c2, move))

        # easy 4cyklus
        r1 = new_cube(solved, "L", LEFT + DOWN)
        r2 = new_cube(solved, "R", DOWN + RIGHT)
        r3 = new_cube(r1, "R", RIGHT + DOWN)
        add_edge(r2, r3, "L")

        # r1 bude základem 6cyklu
        # nejdriv levo prave steny
        s1 = new_cube(solved, "L'", LEFT + UP)
        s2 = new_cube(s1, "R2", LEFT)
        # pak hordolni
        s3 = new_cube(s2, "U2", LEFT)
        s4 = new_cube(s3, "D2", LEFT)
        # a ted z druhe strany, nejdriv hordolni
        s5 = new_cube(r1, "U2", LEFT)
        s6 = new_cube(s5, "D2", LEFT)
        s7 = new_cube(s6, "L2", LEFT)
        add_edge(s7, s4, "R2")

        # + kratky cyklus
        t0 = new_cube(r2, "R", UP + RIGHT)
        t1 = new_cube(t0, "L'", UP + LEFT)
        add_edge(t1, s1, "R2")
        add_edge(solved, t0, "R2")

        # ted chci udelat neco vedle typka ze ktereho budeme hledat
        # tim je s7
        scrambled = s7
        u1 = new_cube(scrambled, "L", DOWN)
        add_edge(u1, s6, "L")

        # dalsi cyklus co vede z r1 do s6
        v1 = new_cube(r1, "F2", DOWN)
        v2 = new_cube(v1, "B2", DOWN)
        v3 = new_cube(v2, "D2", LEFT)
        v4 = new_cube(v3, "U2", LEFT)
        v5 = new_cube(v4, "B2", UP)
        add_edge(v5, s6, "F2")

        # nejdelsi cyklus z r2
        w1 = new_cube(r2, "F'", RIGHT)
        w2 = new_cube(w1, "B2", RIGHT)
        w3 = new_cube(w2, "F'", RIGHT)
        w4 = new_cube(w3, "U2", RIGHT)
        w5 = new_cube(w4, "D2", DOWN)

        w6 = new_cube(r2, "U'", DOWN)
        w7 = new_cube(w6, "D2", RIGHT)
        w8 = new_cube(w7, "U'", RIGHT)
        w9 = new_cube(w8, "F2", RIGHT)
        add_edge(w9, w5, "B2")

        # nakonec par nahodnych hran
        n1 = new_cube(t0, "F", RIGHT, True)
        n2 = new_cube(n1, "L'", RIGHT, True)
        n3 = new_cube(n1, "U", UP, True)
        n4 = new_cube(n2, "U'", UP, True)

        n5 = new_cube(s1, "D", UP, True)
        n6 = new_cube(s2, "F'", UP, True)
        n7 = new_cube(s3, "R", UP, True)

        n8 = new_cube(n6, "L'", UP + LEFT, True)
        n9 = new_cube(n6, "R2", UP + RIGHT, True)

        n10 = new_cube(s7, "F", LEFT + UP, True)
        n11 = new_cube(s7, "L'", LEFT, True)
        n12 = new_cube(n11, "R'", LEFT + DOWN, True)
        n13 = new_cube(n11, "L'", DOWN, True)
        add_edge(n13, u1, "L'")
        n14 = new_cube(n10, "R", UP, True)

        n15 = new_cube(t1, "F'", UP, True)
        n16 = new_cube(t1, "U", UP + RIGHT, True)

        n17 = new_cube(w6, "F", DOWN, True)
        n18 = new_cube(n17, "L", RIGHT, True)
        n19 = new_cube(n17, "U'", LEFT, True)

        # rozhazeni kostek do prostoru
        positions = [c.get_center() / 1.0 for c in nodes]
        posedges = [(nodes.index(u), nodes.index(v)) for u, v in edges]

        # small score means graph is scattered
        def score():
            sc = 0.0

            for i in range(len(positions)):
                Delta = -1
                if i in can_be_outside:
                    Delta = 0

                pos = positions[i]
                if (
                    pos[0] < -(7 + Delta)
                    or pos[0] > (7 + Delta)
                    or pos[1] < -(4 + Delta)
                    or pos[1] > (4 + Delta)
                ):
                    return float("inf")

            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    sc += 1 / (norm(positions[i] - positions[j]) ** 2)

            for i, j in posedges:
                sc -= 1 / (2 * (norm(positions[i] - positions[j]) ** 2))

            return sc

        # randomly shift nodes until the graph is scattered
        if False:
            if score() == float("inf"):
                positions = [pos / 1.2 for pos in positions]

            length = 100
            for l in range(length):
                i = random.randrange(0, len(positions))

                if i == 0:
                    continue
                delta = 1 - l * 1.0 / length
                move = np.array(
                    [random.uniform(-delta, delta), random.uniform(-delta, delta), 0]
                )
                oldscore = score()

                oldpos = positions[i].copy()
                positions[i] += move
                newscore = score()

                if newscore > oldscore:
                    positions[i] = oldpos

        # animate creation of the graph

        self.add(solved)

        created = set()
        created.add(solved)
        cubes_on_scene = [solved]

        while anims_to_do:
            print(len(anims_to_do))
            anims = []
            active = set()
            to_create = set()
            leftover = []
            for (c1, c2, move) in anims_to_do:
                if c1 in created and not c1 in active:
                    cnew = c1.copy()
                    anims += [
                        CubeMove(cnew, move=move, target_position=c2.get_center()),
                        Create(Line(c1.get_center(), c2.get_center())),
                    ]
                    cubes_on_scene.append(cnew)
                    active.add(c1)
                    to_create.add(c2)
                else:
                    leftover.append((c1, c2, move))

            self.play(*anims, run_time=1)
            anims_to_do = leftover
            created = created.union(to_create)

        # change to houses

        self.next_section(skip_animations=True)

        houses = [
            ImageMobject("img/house.png").move_to(c.get_center())
            for c in cubes_on_scene
        ]

        icons = [
            ImageMobject("img/icon.png").move_to(c.get_center()) for c in cubes_on_scene
        ]

        infty = 10000.0
        for c, house, icon in zip(cubes_on_scene, houses, icons):
            house.width = icon.width = c.width
            house.scale(1.0 / infty)
            icon.scale(1.0 / infty)

        # cubes disappear
        anims = []
        for cube in cubes_on_scene:
            anims.append(cube.animate().scale(1.0 / infty))

        self.play(*anims)

        # houses appear and disappear

        self.add(*houses)

        self.play(*[house.animate().scale(infty) for house in houses])

        self.play(*[house.animate().scale(0) for house in houses])
        self.remove(*houses)

        # icons appear and disappear

        self.add(*icons)

        self.play(*[icon.animate().scale(infty) for icon in icons])

        self.play(*[icon.animate().scale(0) for icon in icons])

        self.remove(*icons)

        # cubes appear
        anims = []
        for cube in cubes_on_scene:
            anims.append(cube.animate().scale(infty))

        self.play(*anims)
