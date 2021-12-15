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

#https://colorswall.com/palette/171
cube.DEFAULT_CUBE_COLORS = ["#ffffff", "#b71234", "#009b48", "#ffd500", "#ff5800", "#0046ad"]


class Logo(ThreeDScene):
    def construct(self):
        text_color = GRAY
        buffer_h = 2.7
        buffer_v = 1.3  # pripadne: 1.5
        row_shift = 0.35  # pripadne: 0

        a = []
        for i in range(3):
            row = []
            for j in range(3):
                cur = Tex(r"log", color=text_color)
                cur.scale(4).shift(
                    (j * buffer_h + i * row_shift) * RIGHT + i * buffer_v * DOWN
                )
                row.append(cur)

            a += row

        group = Group(*a)
        group.move_to(ORIGIN)

        if False:
            w, h = 14, 8.2
            w = h
            bg = Polygon(
                np.array([-w / 2, h / 2, 0]),
                np.array([w / 2, h / 2, 0]),
                np.array([-w / 2, -h / 2, 0]),
                color=BASE02,
                fill_opacity=1,
            )

            self.add(bg, *a)


class ChannelIntro(ThreeDScene):
    def construct(self):
        text_color = GRAY

        buffer = 0.7

        rozhon = Tex(
            r"\textbf{Václav Rozhoň}: script, animation", color=text_color
        )
        volhejn = Tex(
            r"\textbf{Václav Volhejn}: voice, script, animation",
            color=text_color,
        ).shift(DOWN * buffer)
        hlasek = Tex(r"\textbf{Filip Hlásek}: code", color=text_color).shift(
            2 * DOWN * buffer
        )

        names = Group(rozhon, volhejn, hlasek)
        names.shift(2 * DOWN + LEFT)

        volhejn.align_to(names, LEFT)
        rozhon.align_to(names, LEFT)
        hlasek.align_to(names, LEFT)

        channel_name = Tex(r"polylog", color=text_color)
        channel_name.scale(4).shift(1 * UP)

        run_time = Write(channel_name).run_time
        self.play(
            Write(volhejn, run_time=run_time),
            Write(rozhon, run_time=run_time),
            Write(hlasek, run_time=run_time),
            Write(channel_name, run_time=run_time),
        )

        self.wait(3)

        self.play(
            Unwrite(volhejn, reverse=True),
            Unwrite(rozhon),
            Unwrite(hlasek),
            Unwrite(channel_name),
            run_time=1,
        )
        self.wait(1)


class MoveDefinition(ThreeDScene):
    def construct(self):
        """
        Co počítáme jako jeden move?

        What counts as one move? Say that for simplicity, we will assume that we
        never rotate the cube as a whole, so the middle cubies will always stay
        in the same place. Then, a move only rotates the sides of the cube: the
        top and bottom, the left and right, and the front and back. Each can be
        rotated to three new positions, hence 18 total possibilities.
        """
        self.camera.set_focal_distance(20000.0)
        self.camera.should_apply_shading = False

        faces = "UDLRFB"
        positions = []

        for dy in range(3):
            for dx in range(-3, 3):
                positions.append([dx + 0.5, -dy - 2, 0])

        first_cube = RubiksCube(cubie_size=1)

        self.play(FadeIn(first_cube))
        self.play(Rotate(first_cube, 2 * PI, UP), run_time=3)

        self.play(first_cube.animate.scale(0.5))

        grid_spacing = 2

        cubes = [RubiksCube(cubie_size=0.5) for i in range(len(faces))]

        self.add(*cubes)
        self.remove(first_cube)

        self.play(
            *[
                cube.animate.shift(RIGHT * grid_spacing * (i - 2.5))
                for i, cube in enumerate(cubes)
            ]
        )

        self.wait()

        self.play(
            *[CubeMove(cube, face + "") for cube, face in zip(cubes, faces)],
            run_time=3,
        )

        self.wait()

        anims = []

        for y in [-1, 1]:
            for i, face in enumerate(faces):
                cubes.append(
                    RubiksCube(rotate_nicely=True, cubie_size=0.5).shift(
                        RIGHT * grid_spacing * (i - 2.5)
                    )
                )
                anims.append(cubes[-1].animate.shift(UP * grid_spacing * y))

        self.add(*cubes)

        self.play(*anims)
        self.wait()

        anims = []

        for j in [2, 0, 1]:
            for i, face in enumerate(faces):
                anims.append(CubeMove(cubes[j * 6 + i], face + ["", "2", "'"][j]))

        self.play(LaggedStart(*anims))
        self.wait(2)


'''
what you see is just a tiny part of the neighborhood
of the solved cube. Remember, every cube has 18
neighbors in the full graph!
'''

class FancyGraph(ThreeDScene):#MovingCameraScene):
    def construct(self):
        self.next_section(skip_animations=False)
        #self.camera.frame.save_state()

        solved = RubiksCube(cubie_size=0.3)



        nodes = [solved]
        edges = []
        can_be_outside = set()
        anims_to_do = []

        def new_cube(cube, move, shift, outside = False):
            c = cube.copy().do_move(move).shift(shift)
            nodes.append(c)
            edges.append((cube, c))
            if outside:
                can_be_outside.add(len(nodes)-1)
            anims_to_do.append((cube,  c, move))
            return c

        def add_edge(c1, c2, move):
            edges.append((c1, c2))
            anims_to_do.append((c1, c2, move))



        #easy 4cyklus
        r1 = new_cube(solved, "L", LEFT + DOWN)
        r2 = new_cube(solved, "R", DOWN + RIGHT)
        r3 = new_cube(r1, "R", RIGHT + DOWN)
        add_edge(r2, r3, "L")

        #r1 bude základem 6cyklu
        #nejdriv levo prave steny
        s1 = new_cube(solved, "L'", LEFT+UP)
        s2 = new_cube(s1, "R2", LEFT)
        #pak hordolni
        s3 = new_cube(s2, "U2", LEFT)
        s4 = new_cube(s3, "D2", LEFT)
        #a ted z druhe strany, nejdriv hordolni
        s5 = new_cube(r1, "U2", LEFT)
        s6 = new_cube(s5, "D2", LEFT)
        s7 = new_cube(s6, "L2", LEFT)
        add_edge(s7, s4, "R2")

        #+ kratky cyklus
        t0 = new_cube(r2, "R", UP+RIGHT)
        t1 = new_cube(t0, "L'", UP+LEFT)
        add_edge(t1, s1, "R2")
        add_edge(solved, t0, "R2")

        #ted chci udelat neco vedle typka ze ktereho budeme hledat
        #tim je s7
        scrambled = s7
        u1 = new_cube(scrambled, "L", DOWN)
        add_edge(u1, s6, "L")

        #dalsi cyklus co vede z r1 do s6
        v1 = new_cube(r1, "F2", DOWN)
        v2 = new_cube(v1, "B2", DOWN)
        v3 = new_cube(v2, "D2", LEFT)
        v4 = new_cube(v3, "U2", LEFT)
        v5 = new_cube(v4, "B2", UP)
        add_edge(v5, s6, "F2")

        #nejdelsi cyklus z r2
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

        #nakonec par nahodnych hran
        n1 = new_cube(t0, "F", RIGHT, True)
        n2 = new_cube(n1, "L'", RIGHT, True)
        n3 = new_cube(n1, "U", UP, True)
        n4 = new_cube(n2, "U'", UP, True)

        n5 = new_cube(s1, "D", UP, True)
        n6 = new_cube(s2, "F'", UP, True)
        n7 = new_cube(s3, "R", UP, True)

        n8 = new_cube(n6, "L'", UP+LEFT, True)
        n9 = new_cube(n6, "R2", UP+RIGHT, True)
        
        n10= new_cube(s7, "F", LEFT + UP, True)
        n11= new_cube(s7, "L'", LEFT, True)
        n12= new_cube(n11, "R'", LEFT+DOWN, True)
        n13= new_cube(n11, "L'", DOWN, True)
        add_edge(n13, u1, "L'")
        n14 = new_cube(n10, "R", UP, True)

        n15 = new_cube(t1, "F'", UP, True)
        n16 = new_cube(t1, "U", UP+RIGHT, True)

        n17 = new_cube(w6, "F", DOWN, True)
        n18 = new_cube(n17, "L", RIGHT, True)
        n19 = new_cube(n17, "U'", LEFT, True)

        #rozhazeni kostek do prostoru
        positions = [c.get_center() / 1.0 for c in nodes]
        posedges = [ (nodes.index(u), nodes.index(v)) for u, v in edges]

        # small score means graph is scattered
        def score():
            sc = 0.0
            
            for i in range(len(positions)):
                Delta = -1
                if i in can_be_outside:
                    Delta = 0
                
                pos = positions[i]
                if pos[0] < -(7+Delta) or pos[0] > (7+Delta) or pos[1] < -(4+Delta) or pos[1] > (4+Delta):
                    return float('inf')
            
            for i in range(len(positions)):
                for j in range(i+1, len(positions)):
                    sc += 1 / (norm(positions[i] - positions[j]) ** 2)
            
            for i, j in posedges:
                sc -= 1 / (2 * (norm(positions[i] - positions[j]) ** 2))


            return sc

        #randomly shift nodes until the graph is scattered
        if False:
            if score() == float('inf'):
                positions = [pos/1.2 for pos in positions]
                    
            length = 100
            for l in range(length):
                i = random.randrange(0, len(positions))
                
                if i == 0:
                    continue
                delta = 1 - l * 1.0 / length
                move = np.array([random.uniform(-delta, delta), random.uniform(-delta, delta), 0])
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
                        CubeMove(cnew,  move = move, target_position = c2.get_center()),
                        Create(Line(c1.get_center(), c2.get_center()))
                    ]
                    cubes_on_scene.append(cnew)
                    active.add(c1)
                    to_create.add(c2)
                else:
                    leftover.append((c1, c2, move))
            
            self.play(
                *anims,
                run_time = 1
            )
            anims_to_do = leftover    
            created = created.union(to_create)

        # change to houses

        self.next_section(skip_animations=False)

        houses = [
            ImageMobject(
                "img/house.png"
            ).move_to(c.get_center())
            for c in cubes_on_scene
        ]

        icons = [
            ImageMobject(
                "img/icon.png"
            ).move_to(c.get_center())
            for c in cubes_on_scene
        ]

        infty = 10000.0
        for c, house, icon in zip(cubes_on_scene, houses, icons):
            house.width = icon.width = c.width 
            house.scale(1.0/infty)
            icon.scale(1.0/infty)

        # cubes disappear
        anims = []
        for cube in cubes_on_scene:
            anims.append(
                cube.animate().scale(1.0 / infty)
            )

        self.play(
            *anims
        )

        # houses appear and disappear
        
        self.add(
            *houses
        )

        self.play(
            *[
                house.animate().scale(infty)
                for house in houses
            ]
        )

        self.play(
            *[
                house.animate().scale(0)
                for house in houses
            ]
        )
        self.remove(
            *houses
        )

        # icons appear and disappear
        
        self.add(
            *icons
        )

        self.play(
            *[
                icon.animate().scale(infty)
                for icon in icons
            ]
        )

        self.play(
            *[
                icon.animate().scale(0)
                for icon in icons
            ]
        )

        self.remove(
            *icons
        )

        # cubes appear
        anims = []
        for cube in cubes_on_scene:
            anims.append(
                cube.animate().scale(infty)
            )

        self.play(
            *anims
        )

class FeliksVsOptimal(ThreeDScene):
    def construct(self):
        """
        For example, with this definition the position that Mr. Zemdegs solved
        can be solved in 18 moves, although Mr. Zemdegs’s solution was of course
        different and used 44 moves.
        """
        self.camera.set_focal_distance(20000.0)
        self.camera.should_apply_shading = False

        cube_distance = 7

        cube_actual = RubiksCube(cubie_size=0.75, rotate_nicely=False).shift(
            LEFT * cube_distance / 2
        )
        cube_best = RubiksCube(cubie_size=0.75, rotate_nicely=False).shift(
            RIGHT * cube_distance / 2
        )

        buff = 1
        text_actual = (
            Tex("Feliks Zemdegs", color=GRAY)
            .scale(1.5)
            .next_to(cube_actual, direction=UP, buff=buff)
        )
        counter_actual = (
            Integer(0, color=GRAY)
            .scale(1.5)
            .next_to(cube_actual, direction=DOWN, buff=buff)
        )
        text_best = (
            Tex("Omniscient being", color=GRAY)
            .scale(1.5)
            .next_to(cube_best, direction=UP, buff=buff)
        )
        counter_best = (
            Integer(0, color=GRAY)
            .scale(1.5)
            .next_to(cube_best, direction=DOWN, buff=buff)
        )

        self.add(text_actual, text_best, counter_actual, counter_best)

        for cube in [cube_best, cube_actual]:
            util.scramble_to_feliks(cube)

            # TODO: tady ty kostky otacim, aby to bylo z Feliksova pohledu, tj. nejvic
            # se pouziva R a U. Zamichany stav kostky ale pak vypada jinak nez v ostatnich
            # castech, kde kostka otocena neni. Vadi nam to?

            # Rotate to get Feliks' POV
            cube.rotate(PI / 2, RIGHT)
            cube.rotate(PI / 2, UP)

            # "rotate nicely"
            cube.rotate(15 * DEGREES, axis=np.array([1, 0, 0]))
            cube.rotate(15 * DEGREES, axis=np.array([0, 1, 0]))

        self.add(cube_best, cube_actual)
        self.wait()

        for i, (move_actual, move_best) in enumerate(
            itertools.zip_longest(
                util.FELIKS_ACTUAL_SOLUTION_MOVES, util.FELIKS_UNSCRAMBLE_MOVES
            )
        ):
            anims_cur = [cube_actual.animate.do_move(move_actual)]
            if move_best is not None:
                anims_cur += [cube_best.animate.do_move(move_best)]
            self.play(*anims_cur, run_time=(10 / (15 + min(40, i ** 2))))

            counter_actual.set_value(i + 1).set_color(GRAY)
            if move_best is not None:
                counter_best.set_value(i + 1).set_color(GRAY)

        self.wait()
        self.play(FadeIn(Tex("cube20.org", color=GRAY)))
        self.wait()


class CubeGraph(ThreeDScene):
    def construct(self):
        """
        TODO: ukázat co myslíme grafem kostky v tomto případě. Ukázat malou část
        grafu (nejspíš ani neukazovat všech 18 hran z vrcholu), každý vrchol
        jedna kostka. Pak v něm vyznačit cestu z nějakého stavu do složeného,
        nejspíš něco triviálního o délce 2.

        In this case, the possible configurations of the cube form the nodes of
        a vast network, with two nodes being connected if there is a move from
        one configuration to the other. In computer science, we call such
        networks graphs and the connections edges. Thinking in terms of graphs
        is a common trick, since it can stand for a road network, or friendships
        on a social network, or, in our case an abstract network of
        configurations.

        So let’s say we want to solve our cube with as few moves as possible. In
        the language of graphs, this amounts to finding the shortest path from
        the scrambled configuration to the solved one.

        So how can we find the shortest path? The first solution that comes to
        mind is to take the scrambled configuration and do what is also called
        the breadth first search algorithm. Simply speaking, this algorithm
        explores all possible configurations from the scrambled one in the order
        of their distance to that configuration. We are searching until we
        encounter the solved configuration.
        """
        self.camera.set_focal_distance(20000.0)
        self.camera.should_apply_shading = False

        # TODO: najit zajimavejsi graf, ve kterem existuji dve cesty (dve reseni)
        # ktere se netrivialne lisi a jedna je rychlejsi.
        vertices = [
            1,  # solved
            2,  # R
            3,  # L2
            4,  # L2 R
            5,  # R U'
        ]
        edges = [(1, 2), (1, 3), (2, 4), (3, 4), (5, 2)]
        g = Graph(
            vertices,
            edges,
            vertex_type=RubiksCube,
            vertex_config={
                "cubie_size": 0.3,
            },
            edge_config={
                "color": GRAY,
                "shade_in_3d": True,  # Needed to keep the edges behind the cube
            },
            layout="kamada_kawai",
        )
        g[2].do_move("R")
        g[3].do_move("L2")
        g[4].do_move("L2").do_move("R")
        g[5].do_move("R").do_move("U'")

        # self.play(Create(g))
        self.add(g)

        self.wait()

        self.play(
            g[1].animate.move_to([1, 1, 0]),
            g[2].animate.move_to([-1, 1, 0]),
            g[3].animate.move_to([1, -1, 0]),
            g[4].animate.move_to([-1, -1, 0]),
        )
        self.wait()

        # TODO: zvyraznit nejkratsi cestu

        # TODO: vizualizovat BFS (podobne jako v prvnim videu)


class NumberOfStates(Scene):
    def construct(self):
        """
        So can this work? Let’s try to find some basic parameters of Rubik’s
        cube. A quick Wikipedia search shows that the number of its states
        reachable from the starting one is exactly 43252003274489856000 which is
        roughly 10^20.

        So in the worst case, our algorithm will have to explore about 10^20
        cube configurations until it finds a solution. That’s a lot! A computer
        can explore roughly 10^6 configurations per second, so this would take
        10^14 seconds, or millions of years. The limit of what we can possibly
        explore with a normal computer in reasonable time is around 10^10 cube
        states, the time to explore this number of configurations should be,
        say, a few hours. Although 10^10 is also a huge number it is laughably
        small if you compare it with 10^20.
        """
        parts_s = ["43", "252", "003", "274", "489", "856", "000"]
        scale_coef = 1.1
        scale_base = 2.0

        parts = [
            Tex(p, color=GRAY).scale(scale_base * scale_coef ** (len(parts_s) - 1 - i))
            for i, p in enumerate(parts_s)
        ]
        group = Group()

        for i, part in enumerate(parts):
            if i > 0:
                part.next_to(
                    parts[i - 1], buff=0.3 * scale_coef ** (len(parts_s) - 1 - i)
                )
            self.play(Write(part))
            group.add(part)
            if i > 0:
                self.play(
                    group.animate.shift(-group.get_center()).scale(1 / scale_coef),
                    run_time=0.3,
                )

        self.wait()

        ten_to_twenty = MathTex(r"\approx 10^{20}", color=GRAY).scale(scale_base)
        ten_to_twenty.next_to(group, direction=DOWN).align_to(group, RIGHT)
        self.play(Write(ten_to_twenty))

        self.wait()
        self.play(group.animate.shift(UP * 2.5), ten_to_twenty.animate.shift(UP * 2.5))
        self.wait()

        ten_to_ten_decimal = (
            MathTex(r"10\,000\,000\,000", color=GRAY)
            .scale(scale_base)
            .align_to(group, RIGHT)
            .shift(DOWN * 1.3)
        )
        ten_to_ten_scientific = (
            MathTex(r"= 10^{10}", color=GRAY)
            .scale(scale_base)
            .next_to(ten_to_ten_decimal, direction=DOWN)
            .align_to(group, RIGHT)
        )

        self.play(Write(ten_to_ten_decimal))
        self.play(Write(ten_to_ten_scientific))
        self.wait()
