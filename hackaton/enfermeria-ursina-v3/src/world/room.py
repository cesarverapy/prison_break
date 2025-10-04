from ursina import Entity, Vec3, color

TILE        = 1.8
WALL_HEIGHT = 3.0
CEILING_Y   = WALL_HEIGHT + 0.4

PARED = color.rgb(205,210,215)
PISO  = color.rgb(185,193,200)

class Room:
    def __init__(self):
        self.floor = Entity(
            model='plane',
            scale=Vec3(1,1,1),
            color=color.white,
            texture='assets/textures/floor_tile.png',
            texture_scale=(15,15),
            collider='box',
            shadow=True
        )
        self.ceiling = Entity(
            model='plane',
            scale=Vec3(1,1,1),
            position=(0, CEILING_Y, 0),
            rotation=(180,0,0),
            texture='assets/textures/ceiling_tile.png',
            color=color.white,
            shadow=False
        )
        self.walls = []
        self.bed = Entity(model='cube', position=(6, WALL_HEIGHT*0.083, 0),
                          scale=(3, 0.5, 1.2), texture='assets/textures/bed_sheet.png',
                          collider='box', shadow=True)
        self.headboard = Entity(model='cube', position=(7.3, WALL_HEIGHT*0.233, 0),
                                scale=(0.2, 1.2, 1.2), color=PARED, shadow=True)

    def build_from_ascii(self, grid: list[str], origin=(0,0,0)):
        rows = len(grid)
        cols = max(len(r) for r in grid)

        self.floor.scale   = Vec3(cols*TILE, 1, rows*TILE)
        self.ceiling.scale = Vec3(cols*TILE, 1, rows*TILE)
        self.ceiling.y     = CEILING_Y

        for r, row in enumerate(grid):
            for c, ch in enumerate(row):
                if ch == '#':
                    x, z = self.tile_to_world_xz(c, r, cols, rows, origin)
                    wall = Entity(
                        model='cube',
                        position=(x, WALL_HEIGHT/2, z),
                        scale=(TILE, WALL_HEIGHT, TILE),
                        texture='assets/textures/wall_panel.png',
                        color=color.white,
                        collider='box',
                        shadow=True
                    )
                    self.walls.append(wall)

    @staticmethod
    def tile_to_world_xz(c, r, cols, rows, origin=(0,0,0)):
        ox, oy, oz = origin
        x = (c - cols/2) * TILE + ox
        z = (rows/2 - r) * TILE + oz
        return x, z

    @staticmethod
    def tile_to_world(c, r, cols, rows, origin=(0,0,0)):
        x, z = Room.tile_to_world_xz(c, r, cols, rows, origin)
        return (x, 0, z)
