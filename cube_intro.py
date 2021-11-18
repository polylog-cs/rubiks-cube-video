from manim import *
import manim

# Use our fork of manim_rubikscube!
from manim_rubikscube import *

# This also replaces the default colors
from solarized import *

import util

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
        TODO: zároveň otáčet a pohybovat kostkou, ukázat všech 18 možných moves

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

        first_cube = RubiksCube(rotate_nicely=True, cubie_size=1)

        self.play(FadeIn(first_cube))
        self.play(Rotate(first_cube, 2 * PI, UP), run_time=3)

        # shift_by = UP * 3

        self.play(first_cube.animate.scale(0.5))

        grid_spacing = 2

        cubes = [
            RubiksCube(rotate_nicely=True, cubie_size=0.5) for i in range(len(faces))
        ]

        self.add(*cubes)
        self.remove(first_cube)

        self.play(
            *[
                cube.animate.shift(RIGHT * grid_spacing * (i - 2.5))
                for i, cube in enumerate(cubes)
            ]
        )

        self.wait()

        # TODO: dát místo linear interpolace něco hladčího?
        for _ in range(4):
            self.play(
                *[
                    CubeMove(cube, face, rate_func=linear)
                    for cube, face in zip(cubes, faces)
                ],
                run_time=0.5
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
        TODO: srovnat nejrychlejší řešení na čas a počet otočení

        For example, with this definition the position that Mr. Zemdegs solved
        can be solved in 18 moves, although Mr. Zemdegs’s solution was of course
        different and used 44 moves.
        """
        pass


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
        TODO: vizualizovat čísla zmíněná okolo počtu stavů. Pro zkrášlení můžeme
        přidat nějakou kostku co se tam bude prostě náhodně otáčet.
        (Pak by superclass musel být ThreeDScene místo Scene)

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
        pass


class Neighborhood(ThreeDScene):
    def construct(self):
        """
        TODO: ukázat graf stavů z nějakého konkrétního do hloubky 1, pak 2, pak
        3 (pokud to půjde). Do hloubky 3 už asi nemůžeme ukazovat v každém
        vrcholu kostku.
        """
        pass


class NeighborCount(Scene):
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
        """
        pass


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
