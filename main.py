from ursina import *
from ursina.shaders import lit_with_shadows_shader
import random
from scenes.scene_manager import SceneManager
from scenes.level1 import Level1Scene

# =========================
# 1) APP INITIALIZATION
# =========================

app = Ursina()

# Setup random seed for consistent behavior
random.seed(0)
Entity.default_shader = lit_with_shadows_shader

# =========================
# 2) SCENE MANAGEMENT
# =========================

# Create scene manager
scene_manager = SceneManager()
scene_manager.setup(app)

# Register available scenes/levels
scene_manager.register_scene('level1', Level1Scene)
# TODO: Register more levels as they are created
# scene_manager.register_scene('level2', Level2Scene)
# scene_manager.register_scene('level3', Level3Scene)

# =========================
# 3) GLOBAL CALLBACKS
# =========================

def update():
    """Global update callback"""
    scene_manager.update()

def input(key):
    """Global input callback"""
    scene_manager.input(key)

# =========================
# 4) GAME START
# =========================

# Load the first level
scene_manager.load_scene('level1')

# =========================
# 5) RUN GAME
# =========================

if __name__ == "__main__":
    app.run()