from ursina import color, Text, held_keys, held_keys
from ursina.prefabs.first_person_controller import FirstPersonController

from src.gameplay.tasks import Task, TaskManager
from src.gameplay.rules import ClinicalRules
from src.ui.hud import HUD
from src.world.room import Room, WALL_HEIGHT, TILE
from src.world.interactables import Sink, MedCart, Patient, Door
from src.levels.loader import load_level_yaml, load_ascii_map

class Game:
    def __init__(self, level_path: str | None = None, ascii_map_path: str | None = None):
        self.tm = TaskManager([
            Task('lavado_manos', 'Lávate las manos en el lavabo'),
            Task('recoger_meds', 'Recoge la medicación del carro', requires=['lavado_manos']),
            Task('administrar',  'Administra la medicación al paciente', requires=['lavado_manos','recoger_meds'])
        ])
        self.rules = ClinicalRules(enforce_handwash=True)
        self.hud = HUD()
        self.meds_in_hand = False

        self.room = Room()

        self.sink = Sink(model='cube', position=(2, 0.45, 3), scale=(1.8, 0.9, 0.8),
                         color=color.white, collider='box', shadow=True)
        self.med_cart = MedCart(model='cube', position=(0, 0.7, 6), scale=(1.6, 1.4, 1.0),
                                texture='assets/textures/cart_blue.png', collider='box', shadow=True)
        self.patient = Patient(model='cube', color=color.rgb(255, 230, 230),
                               position=(6, 1.1, 0), scale=(0.6, 1.1, 0.6), collider='box', shadow=True)
        Text(parent=self.med_cart, text='Carro', y=1.2, x=-0.3, scale=1, color=color.black, background=True)
        Text(parent=self.patient, text='Paciente', y=1.0, x=-0.5, scale=1, color=color.black, background=True)

        self.player = FirstPersonController(y=1.1, speed=6)
        self.player.jump_height = 0.8
        self.player.camera_pivot.y = 1.7
        self.player.position = (0, 1.1, 0)

        self.doors = []

        if ascii_map_path:
            data = load_ascii_map(ascii_map_path)
            grid, spawns = data['grid'], data['spawns']
            doors = data.get('doors', [])
            self.room.build_from_ascii(grid, origin=(0,0,0))
            rows, cols = len(grid), max(len(r) for r in grid)

            def place(ent_name, ent):
                pos = spawns.get(ent_name)
                if pos:
                    c, r = pos
                    x, _, z = self.room.tile_to_world(c, r, cols, rows)
                    ent.position = (x, ent.y, z)

            place('sink', self.sink)
            place('med_cart', self.med_cart)
            place('patient', self.patient)

            # Colocar jugador si hay spawn definido (CORREGIDO: nada de concatenar tuplas)
            ppos = spawns.get('player') or spawns.get('jugador') or spawns.get('spawn_player')
            if ppos:
                c, r = ppos
                px, _, pz = self.room.tile_to_world(c, r, cols, rows)
                self.player.position = (px, 1.1, pz)
            else:
                # SAFE SPAWN SEARCH
                best = None
                def is_open(cc, rr):
                    if rr < 0 or rr >= rows or cc < 0 or cc >= len(grid[rr]):
                        return False
                    return grid[rr][cc] != '#'
                for rr in range(rows):
                    for cc in range(len(grid[rr])):
                        if not is_open(cc, rr):
                            continue
                        dmin = 999
                        for rr2 in range(max(0, rr-2), min(rows, rr+3)):
                            for cc2 in range(max(0, cc-2), min(len(grid[rr2]), cc+3)):
                                if grid[rr2][cc2] == '#':
                                    d = abs(rr2-rr) + abs(cc2-cc)
                                    dmin = min(dmin, d)
                        score = dmin
                        if best is None or score > best[0]:
                            best = (score, cc, rr)
                if best:
                    _, cc, rr = best
                    px, _, pz = self.room.tile_to_world(cc, rr, cols, rows)
                    self.player.position = (px, 1.1, pz)

            def is_wall(c, r):
                if r < 0 or r >= rows or c < 0 or c >= len(grid[r]):
                    return False
                return grid[r][c] == '#'

            # Puertas
            for (c, r) in doors:
                horizontal = is_wall(c-1, r) or is_wall(c+1, r)
                orientation_y = 0 if horizontal else 90

                x0, _, z0 = self.room.tile_to_world(c, r, cols, rows)
                ox, oz = 0.0, 0.0
                half = TILE * 0.5
                eps  = TILE * 0.02
                if orientation_y == 0:
                    if is_wall(c-1, r):
                        ox = -half + eps
                    elif is_wall(c+1, r):
                        ox =  half - eps
                else:
                    if is_wall(c, r-1):
                        oz =  half - eps
                    elif is_wall(c, r+1):
                        oz = -half + eps

                dpos = (x0 + ox, WALL_HEIGHT/2, z0 + oz)

                hinge = 'left'
                if orientation_y == 0:
                    left_wall  = is_wall(c-1, r)
                    right_wall = is_wall(c+1, r)
                    if left_wall and not right_wall:  hinge = 'left'
                    elif right_wall and not left_wall: hinge = 'right'
                else:
                    up_wall   = is_wall(c, r-1)
                    down_wall = is_wall(c, r+1)
                    if up_wall and not down_wall:     hinge = 'left'
                    elif down_wall and not up_wall:   hinge = 'right'

                door = Door(position=dpos, orientation_y=orientation_y, hinge=hinge)
                self.doors.append(door)

        if level_path:
            try:
                data = load_level_yaml(level_path)
                titles = data.get('tasks') or {}
                for t in self.tm.tasks:
                    if t.id in titles:
                        t.title = titles[t.id]
            except Exception as e:
                self.hud.set_prompt(f'Error cargando nivel: {e}')

        self.on_task_progress(initial=True)


    def update(self):
        """Muestra acciones posibles y gestiona interacción (puertas > tareas)."""
        actions = []
        target = None

        # --- Puertas cercanas (prioridad) ---
        for d in getattr(self, 'doors', []):
            try:
                if d.can_interact(self.player):
                    actions.append('E — ' + (getattr(d, 'prompt', 'Abrir/Cerrar puerta') or 'Abrir/Cerrar puerta'))
                    target = d
                    break
            except Exception:
                pass

        # --- Lavar manos ---
        if target is None:
            t_wash = self.tm._get('lavado_manos')
            if t_wash and not t_wash.done and getattr(self, 'sink', None) and self.sink.can_interact(self.player):
                actions.append('E — Lavarte las manos')
                target = self.sink

        # --- Recoger medicación ---
        if target is None:
            t_pick = self.tm._get('recoger_meds')
            if t_pick and not t_pick.done and getattr(self, 'med_cart', None) and self.med_cart.can_interact(self.player):
                if not getattr(self, 'meds_in_hand', False):
                    actions.append('E — Recoger medicación del carro')
                else:
                    actions.append('Ya llevas la medicación')
                target = self.med_cart

        # --- Administrar al paciente ---
        if target is None:
            t_admin = self.tm._get('administrar')
            if t_admin and not t_admin.done and getattr(self, 'patient', None) and self.patient.can_interact(self.player):
                if getattr(self, 'meds_in_hand', False):
                    actions.append('E — Administrar medicación al paciente')
                    target = self.patient
                else:
                    actions.append('No llevas la medicación')

        # Mostrar/ocultar acciones
        if actions:
            self.hud.set_actions(actions)
        else:
            self.hud.set_prompt('')

        # Ejecutar interacción
        if target and held_keys['e']:
            try:
                target.on_interact(self)
            except Exception as e:
                self.hud.set_prompt(f'Error interacción: {e}')
            return

        # Mensaje final si todo está completo
        if self.tm._get('administrar').done:
            self.hud.set_prompt('¡Todas las tareas completadas!')

    def on_task_progress(self, initial: bool = False):
        d, t = self.tm.progress()
        self.hud.set_progress(d, t)
        # Ya no mostramos lista de objetivos
