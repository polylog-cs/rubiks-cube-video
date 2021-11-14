from manim import *

# Use our fork of manim_rubikscube!
from manim_rubikscube import *

# This also replaces the default colors
from solarized import *

import util

cube.DEFAULT_CUBE_COLORS = [BASE3, RED, GREEN, YELLOW, ORANGE, BLUE]


class BasicExample(ThreeDScene):
    def construct(self):
        cube = RubiksCube()

        state = "BBFBUBUDFDDUURDDURLLLDFRBFRLLFFDLUFBDUBBLFFUDLRRRBLURR"
        cube.set_state(state)

        axes = ThreeDAxes()

        self.add(Text("x").shift(np.array([4, 0, 0])))
        self.add(Text("y").shift(np.array([0, 4, 0])))
        self.add(Text("z").shift(np.array([0, 0, 4])))

        cube.rotate(15 * DEGREES, axis=np.array([1, 0, 0]))
        cube.rotate(15 * DEGREES, axis=np.array([0, 1, 0]))

        self.play(CubeMove(cube, "L"), run_time=1)
        self.play(CubeMove(cube, "R"), run_time=1)
        self.play(CubeMove(cube, "U"), run_time=1)
        self.play(CubeMove(cube, "D"), run_time=1)
        self.play(CubeMove(cube, "F"), run_time=1)
        self.play(CubeMove(cube, "B"), run_time=1)

        self.wait(1)


class CubeAndGraph(ThreeDScene):
    def construct(self):
        vertices = [1, 2, 3, 4]
        edges = [(1, 2), (2, 3), (3, 4), (1, 3), (1, 4)]
        g = Graph(
            vertices,
            edges,
            vertex_type=RubiksCube,
            vertex_config={
                "cubie_size": 0.5,
                "rotate_nicely": True,
            },
        )
        self.play(Create(g))
        self.wait()
        self.play(
            g[1].animate.move_to([1, 1, 0]),
            g[2].animate.move_to([-1, 1, 0]),
            g[3].animate.move_to([1, -1, 0]),
            g[4].animate.move_to([-1, -1, 0]),
        )
        self.wait()

        self.wait(1)


class MoveDefinition(ThreeDScene):
    def construct(self):
        self.camera.set_focal_distance(20000.0)

        moves = [pre + suf for suf in ["", "'", "2"] for pre in "RLUDFB"]
        print(moves)
        positions = []

        for dy in range(3):
            for dx in range(-3, 3):
                positions.append([dx + 0.5, -dy - 2, 0])

        cur_cube = RubiksCube(rotate_nicely=True, cubie_size=1)

        print("Outer:", cur_cube.get_sheen_factor(), cur_cube.get_sheen_direction())

        self.play(FadeIn(cur_cube))
        # self.play(Rotate(cur_cube, 2 * PI, UP), run_time=3)
        self.play(Rotate(cur_cube, 2 * PI, UP), run_time=1)
        self.wait(0.5)
        return
        shift_by = UP * 3

        def scale_and_shift(cube: RubiksCube):
            cube.shift(shift_by)
            cube.scale(0.3)
            return cube

        self.play(ApplyFunction(scale_and_shift, cur_cube))

        for move, position in zip(moves[:6], positions[:6]):
            new_cube = RubiksCube(rotate_nicely=True, cubie_size=0.3)
            new_cube.shift(shift_by)
            self.add(new_cube)
            cur_cube.set_opacity(0)

            def do_move(cube: RubiksCube):
                cube.set_opacity(1)
                cube.shift(np.array(position) * 1.5)
                return cube

            self.play(ApplyFunction(do_move, cur_cube))
            self.play(CubeMove(cur_cube, move))
            cur_cube = new_cube

        self.wait(1)


def bfs_circle_animations(
    center,
    iterations,
    label_angle=0.25 * PI,
    group=None,
    base_radius=0.9,
    radius_step=0.4,
):
    if group is None:
        group = Group()

    circle = Circle(color=RED, radius=base_radius).move_to(center)

    tex = MathTex(r"1", color=RED)

    tex.add_updater(
        lambda x: x.move_to(
            Point()
            .move_to(circle.get_right() + RIGHT * 0.4)
            .rotate(angle=label_angle, about_point=circle.get_center()),
        )
    )
    group.add(circle, tex)

    yield (GrowFromCenter(circle), FadeIn(tex))

    for i in range(1, iterations):
        c2 = circle.copy()
        group.add(c2)

        # This is needed so that the label follows properly during the animation
        # (we can't be moving `c2`, it has to be `circle`)
        circle, c2 = c2, circle

        tex2 = MathTex(str(i + 1), color=RED)

        c3 = Circle(color=RED, radius=base_radius + i * radius_step).move_to(center)

        yield (
            circle.animate.become(c3),
            c2.animate.set_color(GRAY),
            tex.animate.become(tex2),
        )

    tex.clear_updaters()


class MeetInTheMiddle(ThreeDScene):
    def construct(self):
        self.camera.set_focal_distance(20000.0)
        cube_distance = 8
        cube_from = RubiksCube(cubie_size=0.3, rotate_nicely=True).shift(
            LEFT * cube_distance / 2
        )
        cube_to = RubiksCube(cubie_size=0.3, rotate_nicely=True).shift(
            RIGHT * cube_distance / 2
        )
        util.scramble_to_feliks(cube_from)

        self.add(cube_from, cube_to)

        self.wait()

        base_radius = 0.9
        radius_step = 0.3
        n_steps = 10

        group_from = Group(cube_from)
        group_to = Group(cube_to)

        for anims_from, anims_to in zip(
            bfs_circle_animations(
                cube_from.get_center(),
                n_steps,
                label_angle=0.25 * PI,
                group=group_from,
                base_radius=base_radius,
                radius_step=radius_step,
            ),
            bfs_circle_animations(
                cube_to.get_center(),
                n_steps,
                label_angle=0.75 * PI,
                group=group_to,
                base_radius=base_radius,
                radius_step=radius_step,
            ),
        ):
            self.play(*anims_from, run_time=0.5)
            self.play(*anims_to, run_time=0.5)

        self.wait()

        coef = 0.5 * cube_distance - (base_radius + radius_step * (n_steps - 1))

        print(0.5 * cube_distance, (base_radius + radius_step * (n_steps - 1)))
        self.play(
            group_from.animate.shift(RIGHT * coef), group_to.animate.shift(LEFT * coef)
        )
        self.wait()


class SheenBug(ThreeDScene):
    """Only for bug report purposes"""

    def construct(self):
        rect = RoundedRectangle(  # Works fine for `Rectangle`
            height=5.0,  # Works fine if width and height are not set
            width=6.0,  # Works fine if width and height are not set
            shade_in_3d=True,
            # sheen_factor=0.0, # Doesn't do anything
            fill_opacity=1.0,
        )

        rect.set_fill(BLUE)

        self.add(rect)
        self.play(
            Rotate(
                rect,
                about_point=np.array([0, 0, -1]),
                axis=np.array([0, 1, 0]),
                angle=2 * PI,
            ),
            run_time=3,
            rate_func=linear,
        )
        self.wait(1)
