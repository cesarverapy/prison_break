from src.core.app import make_app
from src.game import Game

if __name__ == "__main__":
    app = make_app(borderless=False, fov=85)
    game = Game(level_path="data/levels/level1.yaml",
                ascii_map_path="data/levels/ward1.map.txt")
    def update():
        game.update()

    app.run()
