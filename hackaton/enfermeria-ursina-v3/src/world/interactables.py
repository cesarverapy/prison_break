from ursina import Entity, color, curve, Text
from ursina import Vec3 
from src.core.utils import dist2d
from src.world.room import WALL_HEIGHT, TILE

INTERACTIVO = color.rgb(40,110,230)
CRITICO     = color.rgb(230,150,60)

class Interactable(Entity):
    def __init__(self, prompt: str, interact_distance: float = 2.6, **kwargs):
        collider = kwargs.pop('collider', 'box')
        super().__init__(collider=collider, **kwargs)
        self.prompt = prompt
        self.interact_distance = interact_distance

    def can_interact(self, who: Entity) -> bool:
        if getattr(self, 'enabled', True) is False:
            return False
        return dist2d(self, who) <= self.interact_distance

    def on_interact(self, game):
        pass

class Sink(Interactable):
    def __init__(self, **kwargs):
        kwargs.setdefault('collider', 'box')
        super().__init__(prompt='Pulsa E para LAVARTE LAS MANOS', interact_distance=3.2, **kwargs)

    def on_interact(self, game):
        t = game.tm._get('lavado_manos')
        if t and not t.done:
            if game.tm.complete('lavado_manos'):
                self.color = color.rgb(220,255,220)
                game.on_task_progress()

class MedCart(Interactable):
    def __init__(self, **kwargs):
        super().__init__(prompt='Pulsa E para RECOGER la medicación', **kwargs)

    def on_interact(self, game):
        got_handwash = game.tm._get('lavado_manos').done
        rec_meds     = game.tm._get('recoger_meds').done
        if got_handwash and not rec_meds:
            if not game.meds_in_hand:
                game.meds_in_hand = True
                self.color = color.rgb(120,200,255)
                game.tm.complete('recoger_meds')
                game.on_task_progress()
            else:
                game.hud.set_prompt('Ya llevas la medicación')
        elif not got_handwash:
            game.hud.set_prompt('Primero debes lavarte las manos')

class Patient(Interactable):
    def __init__(self, **kwargs):
        super().__init__(prompt='Pulsa E para ADMINISTRAR medicación al paciente', interact_distance=2.2, **kwargs)

    def on_interact(self, game):
        t = game.tm._get('administrar')
        if t and not t.done:
            if game.meds_in_hand and game.rules.may_administer(game.tm):
                game.meds_in_hand = False
                game.tm.complete('administrar')
                self.color = color.rgb(220,255,220)
                game.on_task_progress()
            else:
                msg = 'No llevas la medicación' if not game.meds_in_hand else 'Primero completa los pasos previos'
                game.hud.set_prompt(msg)

class Door(Interactable):
    def __init__(self, orientation_y: float = 0, hinge: str = 'left', open_degs: float = 90, **kwargs):
        defaults = dict(
            model='cube',
            scale=(0.85 * TILE, WALL_HEIGHT, 0.08 * TILE),
            color=color.rgb(235, 240, 245),
            collider='box',
            shadow=True
        )
        defaults.update(kwargs)
        super().__init__(prompt='Pulsa E para ABRIR/CERRAR', interact_distance=2.4, **defaults)

        self.is_open    = False
        self.rot_closed = float(orientation_y)
        self.open_degs  = abs(float(open_degs))
        self.hinge      = hinge if hinge in ('left','right') else 'left'

        self.origin_x   = -0.5 if self.hinge == 'left' else 0.5
        self.rotation_y = self.rot_closed

        self.closed_pos = Vec3(self.x, self.y, self.z)
        self.closed_rot = float(self.rotation_y)

    def on_interact(self, game):
        self.prompt = 'Pulsa E para CERRAR' if not self.is_open else 'Pulsa E para ABRIR'
        self.toggle()

    def toggle(self):
        from ursina import invoke
        if not self.is_open:
            delta = self.open_degs if self.hinge == 'left' else -self.open_degs
            self.animate_rotation_y(self.rot_closed + delta, duration=0.25, curve=curve.linear)
            self.collider = None
            self.is_open = True
        else:
            self.animate_rotation_y(self.closed_rot, duration=0.25, curve=curve.linear)
            invoke(self._restore_collision, delay=0.26)
            self.is_open = False

    def _restore_collision(self):
        self.collider = 'box'
