import itertools

from manim import *
import manim

# Use our fork of manim_rubikscube!
from manim_rubikscube import *

# This also replaces the default colors
from solarized import *

import util

try:
    from tqdm import trange
except ImportError:
    trange = range

cube.DEFAULT_CUBE_COLORS = [BASE3, RED, GREEN, YELLOW, ORANGE, BLUE]


class ChannelIntro(ThreeDScene):
    def construct(self):
        text_color = GRAY

        # TODO: napsat kdo co delal?
        volhejn = Tex(r"Václav Volhejn", color=text_color)
        rozhon = Tex(r"Václav Rozhoň", color=text_color)
        hlasek = Tex(r"Filip Hlásek", color=text_color)

        # TODO: tady je nerovnomerne odradkovani :(
        names = Group(rozhon, volhejn, hlasek).arrange(DOWN)
        names.shift(2 * DOWN + 4 * RIGHT)

        volhejn.align_to(names, RIGHT)
        rozhon.align_to(names, RIGHT)
        hlasek.align_to(names, RIGHT)

        # TODO: logo kanalu?
        channel_name = Tex(r"polylog", color=text_color)
        channel_name.scale(4).shift(1 * UP)

        run_time = Write(channel_name).run_time
        self.play(
            Write(volhejn, run_time=run_time),
            Write(rozhon, run_time=run_time),
            Write(hlasek, run_time=run_time),
            Write(channel_name, run_time=run_time),
        )

        self.wait(1)

        self.play(
            Unwrite(volhejn),
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

        faces = "UDLRFB"
        moves = [pre + suf for suf in ["", "'", "2"] for pre in faces]

        positions = []

        for dy in range(3):
            for dx in range(-3, 3):
                positions.append([dx + 0.5, -dy - 2, 0])

        first_cube = RubiksCube(cubie_size=1)

        self.play(FadeIn(first_cube))
        self.play(Rotate(first_cube, 2 * PI, UP), run_time=3)

        # shift_by = UP * 3

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

        # TODO: dát místo linear interpolace něco hladšího?
        for _ in range(4):
            self.play(
                *[
                    CubeMove(cube, face, rate_func=linear)
                    for cube, face in zip(cubes, faces)
                ],
                run_time=0.5,
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


class FeliksVsOptimal(ThreeDScene):
    def construct(self):
        """
        For example, with this definition the position that Mr. Zemdegs solved
        can be solved in 18 moves, although Mr. Zemdegs’s solution was of course
        different and used 44 moves.
        """
        self.camera.set_focal_distance(20000.0)

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
            self.play(*anims_cur, run_time=(10 / (15 + i)))

            counter_actual.set_value(i + 1).set_color(GRAY)
            if move_best is not None:
                counter_best.set_value(i + 1).set_color(GRAY)

        # TODO: odkazat na cube20.org
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


class Neighborhood(ThreeDScene):
    def construct(self):
        """
        TODO: ukázat graf stavů z nějakého konkrétního do hloubky 1, pak 2, pak
        3 (pokud to půjde). Do hloubky 3 už asi nemůžeme ukazovat v každém
        vrcholu kostku.
        """
        self.camera.set_focal_distance(20000.0)

        self.next_section("First layer", skip_animations=True)

        edges = set()
        q = [RubiksCube(cubie_size=0.2)]
        seen = set([q[0].hash()])
        layers = [[q[0].hash()], []]
        parents = {}
        parents[q[0].hash()] = None

        print("Starting BFS")
        for i in trange(262):  # 1, 19, 262
            old_hash = q[i].hash()

            for move in util.POSSIBLE_MOVES:
                if i < 19:
                    q[i].do_move(move)
                else:
                    # This is faster, but does not rotate visually
                    q[i].update_indices_after_move(move)

                new_hash = q[i].hash()
                edges.add((min(old_hash, new_hash), max(old_hash, new_hash)))

                if new_hash not in parents:
                    parents[new_hash] = old_hash

                if new_hash not in seen:
                    # We won't be showing these anyways, avoid copying
                    if i < 19:
                        q.append(q[i].copy())

                    seen.add(new_hash)
                    layers[-1].append(new_hash)

                if i < 19:
                    q[i].do_move(util.invert_move(move))
                else:
                    q[i].update_indices_after_move(util.invert_move(move))

            if old_hash == layers[-2][-1]:
                layers.append([])

        layout = {layers[0][0]: ORIGIN}

        for li, layer in enumerate(layers[1:]):
            for i, h in enumerate(layer):
                distance = (li + 1) * 3
                pos = distance * UP * np.sin(2 * PI * i / len(layer))
                pos += distance * RIGHT * np.cos(2 * PI * i / len(layer))
                layout[h] = pos

        print(f"Done with BFS, {len(seen)} vertices")

        self.add(q[0])

        anims = []
        cubes1 = []
        for i, move in enumerate(util.POSSIBLE_MOVES):
            cur_cube = q[0].copy()
            cubes1.append(cur_cube)
            anims.append(
                AnimationGroup(
                    # Add 10 * OUT to keep the cubes in front of the edges
                    CubeMove(cur_cube, move, layout[layers[1][i]] + 10 * OUT),
                    Create(
                        Line(ORIGIN, layout[layers[1][i]], shade_in_3d=True, color=GRAY)
                    ),
                    run_time=3,
                )
            )

        self.play(LaggedStart(*anims, lag_ratio=0.01), q[0].animate.shift(10 * OUT))
        anims = []

        for u, v in edges:
            if u in layers[1] and v in layers[1]:

                anims.append(
                    Create(Line(layout[u], layout[v], shade_in_3d=True, color=GRAY))
                )

        for cube in cubes1 + [q[0]]:
            # Dummy animations to keep the cubes on top
            anims.append(cube.animate.shift(ORIGIN))

        self.play(*anims)
        self.wait()

        self.next_section("Second layer", skip_animations=False)

        anims = []

        for i, cube in enumerate(q[19:]):
            h = cube.hash()
            # anims.append(
            #     Create(Dot(layout[h], color=GRAY))
            # )

            def f(cube):
                return cube.move_to(layout[cube.hash()]).set_stroke_width(0).scale(0.2)

            cube.move_to(layout[parents[h]])
            cube.shift(IN * 10)
            self.add(cube)
            # self.bring_to_back(cube)

            anims.append(
                AnimationGroup(
                    ApplyFunction(f, cube),
                    Create(
                        Line(
                            layout[parents[h]],
                            layout[h],
                            shade_in_3d=True,
                            color=GRAY,
                            stroke_width=2,
                        )
                    ),
                )
            )
            # self.add(cube)

        for cube in cubes1 + [q[0]]:
            # Dummy animations to keep the cubes on top
            self.bring_to_front(cube)
            anims.append(cube.animate.shift(ORIGIN))

        self.play(LaggedStart(*anims, lag_ratio=0.001))
        self.wait()

        anims = []
        for u0, v0 in edges:
            # Edges to vertices at distance 3 - ignore these
            if u0 in layers[3] or v0 in layers[3]:
                continue

            # Try both orderings
            for u, v in [(u0, v0), (v0, u0)]:
                if u in layers[2] or v in layers[2]:
                    if u in layers[2]:
                        u, v = v, u

                    # Skip the edge to the parent because we've already created it
                    if u != parents[v]:
                        anims.append(
                            Create(
                                Line(
                                    layout[u],
                                    layout[v],
                                    shade_in_3d=True,
                                    color=GRAY,
                                    stroke_width=2,
                                )
                            )
                        )

        self.play(*anims)
        self.wait()


class BFSTest(ThreeDScene):
    def construct(self):
        """
        Ukázka BFS z jednoho vrcholu, pro testování
        """

        edges = set()
        q = [RubiksCube()]
        seen = set([q[0].hash()])
        layers = [[q[0].hash()], []]

        print("Starting BFS")
        for i in trange(262):
            old_hash = q[i].hash()

            for move in util.POSSIBLE_MOVES:
                q[i].update_indices_after_move(move)
                new_hash = q[i].hash()
                edges.add((min(old_hash, new_hash), max(old_hash, new_hash)))

                if new_hash not in seen:
                    q.append(q[i].copy())
                    seen.add(new_hash)
                    layers[-1].append(new_hash)

                q[i].update_indices_after_move(util.invert_move(move))

            if old_hash == layers[-2][-1]:
                layers.append([])

        layout = {layers[0][0]: ORIGIN}

        for li, layer in enumerate(layers[1:]):
            for i, h in enumerate(layer):
                distance = (li + 1) ** 2
                pos = distance * UP * np.sin(2 * PI * i / len(layer))
                pos += distance * RIGHT * np.cos(2 * PI * i / len(layer))
                layout[h] = pos

        print(f"Done with BFS, {len(seen)} vertices")
        print([len(x) for x in layers])
        graph = Graph(
            list(seen),
            list(edges),
            # layout="kamada_kawai",
            layout=layout,
            vertex_config={"fill_color": GRAY, "radius": 0.04},
            edge_config={"stroke_color": GRAY},
        )
        self.add(graph)
        self.wait()


class NeighborCount(ThreeDScene):
    def construct(self):
        """
        TODO: čísla s počtem vrcholů do vzdálenosti n, pro n = 1, 2, 3. Pak
        ukázat, že je to vždycky zhruba *10.

        Well, one clear property is that the number of reachable configurations
        grows very quickly. We already found out that there are about 10^20 cube
        configurations but people have also computed that every cube can be
        solved in at most 20 moves, so it looks like the number of reachable
        configurations grows by a factor of 10 in every step. At the beginning
        it is a bit faster than that, and the last few steps it is probably
        going to get smaller, but it makes sense to assume it is around 10 every
        step.

        The fact that it grows so quickly is not a matter of course, which we
        will see once we compare the Rubik’s cube graph with a road network
        graph. For example, consider this network of crossroads in Manhattan. In
        this network, the number of nodes explored grows quadratically with the
        distance, whereas for the cube graph it grows exponentially. This means
        that if you explore up to distance 5, the number of nodes visited in
        Manhattan will be around 5^2 = 25. It is roughly twice as much, but that
        is not so important. On the other hand, in the cube graph, the number of
        nodes seen will be around 10^5. Again, it’s actually about 6 times
        larger, but close enough.
        """
        self.camera.set_focal_distance(20000.0)

        self.next_section("Table", skip_animations=False)

        table_group = Group()

        table_values = [
            [0, 1],
            [1, 19],
            [2, 262],
            [3, 3502],
            [4, 46741],
            [5, 621649],
        ]

        def with_thousand_separator(x):
            return f"{x:,d}".replace(",", r"\,")

        table = [[r"\textbf{Steps}", r"\textbf{Explored}"]]
        table += [[with_thousand_separator(x) for x in row] for row in table_values]
        table += [["$n$", r"$\sim 10^n$"]]

        table = [[Tex(x, color=GRAY) for x in row] for row in table]

        for row in table:
            table_group.add(*row)

        horizontal_buff = 0.75
        table_group.arrange_in_grid(
            cols=2,
            col_alignments="rl",
            row_alignments="d" * len(table),
            buff=(horizontal_buff, MED_SMALL_BUFF),
        )

        cube = RubiksCube(cubie_size=0.4)
        # cube.next_to(table_group, direction=UP)

        rubiks_group = Group(cube, table_group)
        rubiks_group.arrange(direction=DOWN, buff=MED_LARGE_BUFF)

        self.play(
            LaggedStart(
                FadeIn(cube),
                *[Write(cell) for row in table[:7] for cell in row],
                lag_ratio=0.1,
            )
        )
        # self.play(
        #     *[AnimationGroup(*[Write(cell) for cell in row]) for row in table_tex[:7]],
        # )
        self.wait()

        for cell in table[-1]:
            cell.set_color(RED).shift(MED_SMALL_BUFF * DOWN)

        self.play(LaggedStart(*[Write(cell) for cell in table[-1]], lag_ratio=0.1))
        self.wait()

        self.next_section("Manhattan comparison", skip_animations=False)

        background_rect = Rectangle(
            height=8,
            width=14.2 / 2,
            fill_opacity=1,
            fill_color=BASE02,
            color=BASE02,
            # shade_in_3d=True,  # for the edges of the graph to be in front
            z_index=-10,
        )

        background_rect.next_to(14.2 / 2 * LEFT, direction=LEFT)
        self.add(background_rect)

        self.play(
            background_rect.animate.move_to(
                # background_rect.get_boundary_point(direction=RIGHT) * RIGHT
                14.2
                / 4
                * LEFT
            ),
            rubiks_group.animate.shift(RIGHT * 14.2 / 4),
            run_time=2,
        )

        self.wait()

        grid_size = 13
        grid_center = grid_size // 2
        grid_spacing = 0.35

        vertices = set((i, j) for i in range(grid_size) for j in range(grid_size))
        distances = {}
        edges = []
        layout = {}
        for i in range(grid_size):
            for j in range(grid_size):
                layout[(i, j)] = np.array([i * grid_spacing, j * grid_spacing, 0.0])
                distances[(i, j)] = abs(i - grid_center) + abs(j - grid_center)

                for cur in [(i + 1, j), (i, j + 1)]:
                    if cur in vertices:
                        edges.append(((i, j), cur))

        graph = Graph(
            vertices,
            edges,
            layout=layout,
            # BASE0 is a bit lighter than BASE00 == GRAY
            vertex_config={"fill_color": GRAY},
            edge_config={"stroke_color": GRAY},
        )
        graph.move_to(LEFT * 14.2 / 4).align_to(rubiks_group, UP)
        self.play(DrawBorderThenFill(graph, run_time=1))
        self.wait()

        dist = 5
        anims = [[] for _ in range(dist + 1)]

        for i in range(grid_size):
            for j in range(grid_size):
                if distances[(i, j)] <= dist:
                    anims[distances[(i, j)]].append(
                        graph.vertices[(i, j)].animate.set_color(RED)
                    )

                for cur in [(i + 1, j), (i, j + 1)]:
                    if cur in vertices:
                        edge_distance = min(distances[(i, j)], distances[cur])
                        if edge_distance < dist:
                            # We don't know the direction of the edge.
                            edge = graph.edges[(((i, j), cur))]
                            anims[edge_distance + 1].append(edge.animate.set_color(RED))

        self.play(
            LaggedStart(
                *[AnimationGroup(*anims_step, run_time=0.25) for anims_step in anims],
                lag_ratio=0.9,
            )
        )

        self.wait()

        values_manhattan = [
            [Tex(r"\textbf{Steps}", color=GRAY), Tex(r"\textbf{Explored}", color=GRAY)],
            [MathTex("5", color=GRAY), MathTex("61", color=GRAY)],
            [MathTex("n", color=RED), MathTex("\sim n^2", color=RED)],
        ]
        table_manhattan = Group(*[cell for row in values_manhattan for cell in row])
        table_manhattan.arrange_in_grid(
            col_alignments="rl",
            row_alignments="ddd",
            buff=(horizontal_buff, MED_SMALL_BUFF),
        )
        for cell in values_manhattan[-1]:
            # The constant is needed because $n^2$ is taller than 10^n
            cell.set_color(RED).shift(MED_SMALL_BUFF * DOWN * 0.6)

        table_manhattan.align_to(rubiks_group, DOWN).shift(14.2 / 4 * LEFT)

        self.play(
            LaggedStart(
                *[Write(cell) for cell in values_manhattan[0]],
                *[Write(cell) for cell in values_manhattan[1]],
                *[Write(cell) for cell in values_manhattan[2]],
                lag_ratio=0.1,
            )
        )

        self.wait()


class FriendshipGraph(Scene):
    def construct(self):
        """
        TODO: ukázat malý friendship graph (Karate Club? Pán prstenů?
        Erdös-Renyi?) a pak v něm udělat BFS, ukázat že malá vzdálenost pokryje
        všechny vrcholy.

        For example, you may have heard about the six degrees of separation
        phenomenon that says that you can reach anybody on earth via 6
        intermediate friends.

        TODO: chceme k tomuhle odstavci nějakou animaci?
        In fact, researchers have verified that, at least on Facebook, you are
        connected to pretty much anybody with just 4 intermediate friends.
        Again, this is because, intuitively, the number of people reached is
        always multiplied by something like 50-100 in every step, since the
        average person has around 100 friends.
        """
        pass
