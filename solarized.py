# background tones (dark theme)

from manim.utils.color import GRAY


BASE03 = "#002b36"
BASE02 = "#073642"
BASE01 = "#586e75"

# content tones

BASE00 = "#657b83"
BASE0 = "#839496"
BASE1 = "#93a1a1"

# background tones (light theme)

BASE2 = "#eee8d5"
BASE3 = "#fdf6e3"

# accent tones

YELLOW = "#d0b700"
YELLOW2 = "#b58900" # The original Solarized yellow
ORANGE = "#c1670c"
ORANGE2 = "#cb4b16" # The original Solarized orange - too close to red
RED = "#dc322f"
MAGENTA = "#d33682"
VIOLET = "#6c71c4"
BLUE = "#268bd2"
CYAN = "#2aa198"
GREEN = "#859900"

# Alias
GRAY = BASE00
GREY = BASE00

from manim import config

config.background_color = BASE2
config.max_files_cached = 1000