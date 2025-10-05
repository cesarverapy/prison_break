from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
import random
from .base_scene import BaseScene


class Level1Scene(BaseScene):
    """Level 1: Prison Cell Escape"""
    
    def setup(self):
        """Initialize Level 1 scene"""
        self.is_active = True
        
        # Create scene entities
        self._create_environment()
        self._create_player()
        self._create_interactive_objects()
        self._create_systems()
        self._wire_up_systems()
        
        print("Level 1: Prison Cell Escape - Ready!")
    
    def _create_environment(self):
        """Create the prison cell environment"""
        # Ground
        ground = Entity(model='plane', collider='box', scale=64, texture='assets/textures/concrete.jpg', texture_scale=(4,4))
        self.entities.append(ground)
        
        # Walls - cell simulator
        # Wall Z=0 (front/interior): 
        wall_1 = Entity(model='cube', collider='box', position=(-8,0,0), scale=(13,8.3,1), rotation=(0,0,0), texture='brick', texture_scale=(5,5))
        self.entities.append(wall_1)
        
        # Wall Z=10 (back): 
        wall_2 = duplicate(wall_1, z=10)
        self.entities.append(wall_2)
        
        # Wall X=-15 (left side):
        wall_3 = Entity(model='cube', collider='box', position=(-15,0,5), scale=(1,8.3,11), rotation=(0,0,0), texture='brick', texture_scale=(5,5))
        self.entities.append(wall_3)
        
        wall_4 = duplicate(wall_2, x=-2, z=5, rotation=(0, 90, 0))
        self.entities.append(wall_4)
        
        # Ceiling:
        ceiling = Entity(model='cube', collider='box', position=(-8.5,4.6,5), scale=(14,1,11), rotation=(0,0,0), texture='brick', texture_scale=(5,5))
        self.entities.append(ceiling)
        
        # Light/sky (simple)
        sun = DirectionalLight()
        sun.look_at(Vec3(1,-1,-1))
        self.entities.append(sun)
        
        sky = Sky()
        self.entities.append(sky)
    
    def _create_player(self):
        """Create the player character"""
        self.player = FirstPersonController(model='cube', position=(-8, 1, 5), color=color.orange, speed=8, collider='box')
        self.player.collider = BoxCollider(self.player, Vec3(0,1,0), Vec3(1,2,1))
        self.entities.append(self.player)
    
    def _create_interactive_objects(self):
        """Create interactive objects in the scene"""
        # Dummy props logic
        self.bed = Entity(model='cube', collider='box', scale=(3.9, 0.5 ,2), color=color.red, position=(-13.5, 0, 1))
        self.bed.tag = 'bed'
        self.entities.append(self.bed)
        
        self.sink = Entity(model='cube', collider='box', scale=(1,1,0.5), color=color.blue, position=(-4, 0, 0.9))
        self.sink.tag = 'sink'
        self.entities.append(self.sink)
        
        self.door = Entity(model='assets/models/door.glb', collider='box', scale=1.0, position=(-8, 0, 9.4), texture='assets/textures/metal.jpg', color=color.rgb(120, 120, 120))
        self.door.tag = 'door'
        self.entities.append(self.door)
        
        self.rejila = Entity(model='cube', scale=(0.8, 0.05, 0.8), position=(-9, 0.025, 1.2), texture='metal.jpg', collider='box')
        self.rejila.tag = 'vent'
        # Ventilation grate hinge to rotate like a lid
        self.rejila.origin = (-self.rejila.scale_x/2, 0, 0)
        self.entities.append(self.rejila)
    
    def _create_systems(self):
        """Create game systems"""
        # Create systems
        self.systems['ui'] = UIManager()
        self.systems['state'] = GameState()
        self.systems['anim'] = AnimationSystem()
        self.systems['inter'] = InteractionSystem(
            player=self.player, 
            ui=self.systems['ui'], 
            state=self.systems['state'], 
            anim=self.systems['anim']
        )
        self.systems['controller'] = GameController(
            player=self.player, 
            pause_handler=None,  # Will be set later
            ui=self.systems['ui'], 
            state=self.systems['state'], 
            anim=self.systems['anim'], 
            inter=self.systems['inter']
        )
        
        # Set up interaction system object references
        self.systems['inter'].bed = self.bed
        self.systems['inter'].sink = self.sink
        self.systems['inter'].vent = self.rejila
        self.systems['inter'].door = self.door
    
    def _wire_up_systems(self):
        """Wire up systems and create pause handler"""
        # Create pause handler
        def pause_input(key):
            if key == 'tab':    # press tab to toggle edit/play mode
                editor_camera = Entity(name='editor_camera', enabled=False, ignore_paused=True)
                editor_camera.enabled = not editor_camera.enabled
                
                self.player.visible_self = editor_camera.enabled
                self.player.cursor.enabled = not editor_camera.enabled
                mouse.locked = not editor_camera.enabled
                editor_camera.position = self.player.position
                
                application.paused = editor_camera.enabled
        
        self.pause_handler = Entity(ignore_paused=True, input=pause_input)
        self.entities.append(self.pause_handler)
        
        # Set pause handler in controller
        self.systems['controller'].pause_handler = self.pause_handler
    
    def update(self):
        """Update scene logic"""
        if self.is_active and self.systems['controller']:
            self.systems['controller'].update()
    
    def input(self, key):
        """Handle input"""
        if self.is_active and self.systems['controller']:
            self.systems['controller'].input(key)


# =========================
# GAME SYSTEMS (EXTRACTED FROM APP.PY)
# =========================

class AnimationSystem:
    def __init__(self):
        self.fade_overlay = Entity(parent=camera.ui, model='quad', color=color.rgba(0,0,0,0), scale=2, z=-0.9)

        self._fade_active = False
        self._fade_dir = 0        # 1: to black, -1: to transparent, 0: idle
        self._fade_t = 0.0
        self._fade_dur = 1.0
        self._fade_cb = None

    def update(self):
        if self._fade_dir == 0:
            return
        # advance normalized time (0..1)
        self._fade_t += (time.dt / self._fade_dur) * (1 if self._fade_dir > 0 else -1)
        if self._fade_dir > 0:
            self.fade_overlay.alpha = clamp(self._fade_t, 0, 1)
            if self._fade_t >= 1.0:
                self._finish_fade()
        else:
            self.fade_overlay.alpha = clamp(self._fade_t, 0, 1)
            if self._fade_t <= 0.0:
                self._finish_fade()

    def _finish_fade(self):
        # complete limit values
        self.fade_overlay.alpha = 1.0 if self._fade_dir > 0 else 0.0
        self._fade_dir = 0
        cb = self._fade_cb
        self._fade_cb = None
        if cb:
            cb()   

    def fade_to_black(self, duration=1.0, callback=None):
        if self._fade_active:    # prevent re-entries
            return
        self._fade_active = True
        self._fade_dir = 1
        self._fade_t = max(0.0, float(self.fade_overlay.alpha or 0.0))
        self._fade_dur = max(0.001, duration)
        self._fade_cb = lambda: (setattr(self, "_fade_active", False), callback and callback())
    
    def fade_in(self, duration=1.0, callback=None):
        if self._fade_active:
            return
        self._fade_active = True
        self._fade_dir = -1
        self._fade_t = min(1.0, float(self.fade_overlay.alpha or 0.0) if self.fade_overlay.alpha is not None else 1.0)
        if self._fade_t == 0.0:
            # if already transparent, force to black so fade-in makes sense
            self.fade_overlay.alpha = 1.0
            self._fade_t = 1.0
        self._fade_dur = max(0.001, duration)
        self._fade_cb = lambda: (setattr(self, "_fade_active", False), callback and callback())

class UIManager:
    def __init__(self):
        self.prompt = Text('', origin=(0,0), scale=1, y=-.45, enabled=False)
        self.msg = Text('', origin=(0,0), scale=1, y=.4, enabled=False)
        self.banner = Text('', origin=(0,0), position=(0,0.25), scale=1.2, background=True, enabled=False)
    
    def show_prompt(self, text):
        self.prompt.text = text
        self.prompt.enabled = True
    
    def hide_prompt(self):
        self.prompt.enabled = False

    def show_feedback(self, text, duration=1.2):
        self.msg.text = text
        self.msg.enabled = True
        invoke(setattr, self.msg, 'enabled', False, delay=duration)
    
    def show_banner(self, text, duration=1.2):
        self.banner.text = text
        self.banner.enabled = True
        invoke(setattr, self.banner, 'enabled', False, delay=duration)

class GameState:
    def __init__(self):
        self.has_key = False
        self.level_completed = False
        self.is_fading = False
    
    def reset(self):
        self.has_key = False
        self.level_completed = False
        self.is_fading = False

class InteractionSystem:
    """Resolves who is the nearest target (proximity) and dispatches actions."""
    def __init__(self, player, ui: UIManager, state: GameState, anim: AnimationSystem):
        self.player = player
        self.ui = ui
        self.state = state
        self.anim = anim
        self.interact_dist = 1.9
        self.current = None
        # messages
        self.msg_bed  = ['Just dust and old springs.', 'Nothing useful here…', 'Firm bed, but not the exit.']
        self.msg_sink = ['Feels hollow behind, but I can\'t move it.', 'Rusty and noisy. Better not force it.', 'Doesn\'t seem like the exit…']

        # entity hooks (assigned from outside)
        self.bed = None
        self.sink = None
        self.vent = None
        self.door = None

    def _nearest(self, entities):
        best_e, best_d = None, 9999
        p = self.player.position
        for e in entities:
            d = distance(e.world_position, p)
            if d < best_d and d <= self.interact_dist:
                best_e, best_d = e, d
        return best_e

    def update(self):
        if application.paused or self.state.is_fading:
            self.ui.hide_prompt()
            return

        ents = [e for e in (self.bed, self.sink, self.vent, self.door) if e is not None]
        tgt = self._nearest(ents)
        self.current = tgt

        if not tgt:
            self.ui.hide_prompt()
            return

        tag = getattr(tgt, 'tag', None)
        if tag == 'bed':
            self.ui.show_prompt('E: Check under the bed')
        elif tag == 'sink':
            self.ui.show_prompt('E: Inspect the sink')
        elif tag == 'vent':
            self.ui.show_prompt('E: Pry the grate')
        elif tag == 'door':
            self.ui.show_prompt('E: Try to open the door')
        else:
            self.ui.hide_prompt()

    def on_interact(self):
        """Call from input('e')."""
        if application.paused or self.state.is_fading or self.current is None:
            return
        tag = getattr(self.current, 'tag', None)

        if tag == 'bed':
            self.ui.show_feedback(random.choice(self.msg_bed))
            return

        if tag == 'sink':
            self.ui.show_feedback(random.choice(self.msg_sink))
            return

        if tag == 'vent':
            if not self.state.has_key:
                self.state.has_key = True
                self.ui.show_feedback('Got the key!')
                try:
                    # simple lid animation
                    self.current.animate_rotation_z(-85, duration=.35, curve=curve.out_cubic)
                except:
                    pass
            else:
                self.ui.show_feedback('I already have the key.')
            return

        if tag == 'door':
            GameController.instance().open_door_sequence()
            return

class GameController:
    """Orchestrates: blocks controls, runs sequences, and delegates to systems."""
    _inst = None
    @staticmethod
    def instance():
        return GameController._inst

    def __init__(self, player, pause_handler, ui: UIManager, state: GameState, anim: AnimationSystem, inter: InteractionSystem):
        GameController._inst = self
        self.player = player
        self.pause_handler = pause_handler
        self.ui = ui
        self.state = state
        self.anim = anim
        self.inter = inter

    def disable_controls(self):
        self.player.enabled = False
        mouse.locked = False
        if self.pause_handler:
            self.pause_handler.enabled = False

    def enable_controls(self):
        self.player.enabled = True
        mouse.locked = True
        if self.pause_handler:
            self.pause_handler.enabled = True

    def update(self):
        # update systems
        self.anim.update()
        self.inter.update()

    def input(self, key):
        if key == 'e':
            self.inter.on_interact()

    # ------- Door Sequence -> Banners -> Fade -------
    def open_door_sequence(self):
        if self.state.level_completed or self.state.is_fading:
            return

        if not self.state.has_key:
            self.ui.show_feedback('🚪 Locked. I need a key.')
            return

        # mark level end
        self.state.level_completed = True
        self.state.is_fading = True
        self.disable_controls()

        # 1) Banner "Door opened…"
        invoke(lambda: self.ui.show_banner('✅ Door opened! You managed to escape the cell.', 1.1), delay=0.05)
        # 2) Banner "Level 1 completed"
        invoke(lambda: self.ui.show_banner('🎉 Level 1 completed!', 1.3), delay=1.20)
        # 3) Fade-out and final callback (closes app; change to next_level if you want)
        invoke(lambda: self.anim.fade_to_black(duration=1.3, callback=lambda: application.quit()), delay=2.60)
