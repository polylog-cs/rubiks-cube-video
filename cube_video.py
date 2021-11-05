from manim import *
# Use our fork of manim_rubikscube!
from manim_rubikscube import *

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

        self.add(cube, axes)

        self.play(CubeMove(cube, "L"), run_time=1)
        self.play(CubeMove(cube, "R"), run_time=1)
        self.play(CubeMove(cube, "U"), run_time=1)
        self.play(CubeMove(cube, "D"), run_time=1)
        self.play(CubeMove(cube, "F"), run_time=1)
        self.play(CubeMove(cube, "B"), run_time=1)

        self.wait(1)

class FixedInFrameMObjectTest(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes()
        # self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)
        text3d = Text("Hello world")
        text3d.to_corner(UL)
        self.add(axes)
        # After creating the RubiksCube, it may be necessary to scale it to
        # comfortably see the cube in the camera's frame
        cube = RubiksCube().scale(0.5)
        # Setup where the camera looks
        # self.move_camera(phi=50 * DEGREES, theta=160 * DEGREES)

        cube2 = RubiksCube().scale(0.5)
        cube2.shift(LEFT * 5)

        # cube.rotate(axis=[1, 1, 1], angle=PI)
        # cube2.rotate(axis=[1, 1, 1], angle=PI)

        # Rotate the camera around the RubiksCube for 8 seconds
        # self.begin_ambient_camera_rotation(rate=0.5)
        # self.camera.frame_center = cube.get_center()
        self.camera.set_phi(0.0)

        self.camera.set_theta(-1.5707963267948966)

        self.camera.set_focal_distance(20000.0)

        self.add_fixed_in_frame_mobjects(text3d)

        self.play(FadeIn(cube, cube2))

        self.wait(1)

        # self.play(CubeMove(cube, "F"), CubeMove(cube2, "L"))
        self.play(CubeMove(cube2, "F"))

        self.wait(1)
