from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
from ursina import destroy
import random
from .base_scene import BaseScene


class Level1Scene(BaseScene):
    """Level 1: Prison Cell Escape"""

    def __init__(self, scene_manager=None):
        super().__init__()
        self.scene_manager = scene_manager
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
        
        # Show watcher's note introduction
        self._show_introduction()
    def _create_environment(self):
        """Create the prison cell environment"""
        # Ground
        ground = Entity(model='plane', collider='box',position=(0,0,-4), scale=60, texture='assets/textures/floor.png', texture_scale=(5,4))
        self.entities.append(ground)
        
        # Walls - cell simulator
        # Wall Z=0 (front/interior): 
        wall_1 = Entity(model='cube', collider='box', position=(-8,0,0), scale=(13,8.3,1), rotation=(0,0,0), texture='assets/textures/walls.png', texture_scale=(4,1))
        self.entities.append(wall_1)
        
        # Wall Z=10 (back): 
        wall_2 = duplicate(wall_1, z=10)
        self.entities.append(wall_2)
        
        # Wall X=-15 (left side):
        wall_3 = Entity(model='cube', collider='box', position=(-15,0,5), scale=(1,8.3,11), rotation=(0,0,0), texture='assets/textures/walls.png', texture_scale=(4,1))
        self.entities.append(wall_3)
        
        wall_4 = duplicate(wall_2, x=-2, z=5, rotation=(0, 90, 0))
        self.entities.append(wall_4)
        
        # Ceiling:
        ceiling = Entity(model='cube', collider='box', position=(-8.5,4.6,5), scale=(14,1,11), rotation=(0,0,0), texture='assets/textures/walls.png', texture_scale=(3,1))
        self.entities.append(ceiling)
        
        # Basic lighting setup
        # Simple directional light (like the original)
        sun = DirectionalLight()
        sun.look_at(Vec3(-1,-1,-1))
        self.entities.append(sun)

        # Cell static items

        # Penguin
        #penguin = Entity(model='assets/models/penguin.glb', collider='box', position=(-10, 0, 6), scale=(0.5, 0.5, 0.5), rotation=(0, 0, 0))
        penguin = Entity(model='assets/models/penguin_plush.glb', collider='box', position=(-13, 0.2 ,9), scale=(0.5, 0.5, 0.5), rotation=(0, 0, 0))
        self.entities.append(penguin)

        poster1 = Entity(model='assets/models/science_poster.glb', collider='box', position=(-14.32, 2, 8), scale=(3, 3, 3), rotation=(0, -90, 0))
        self.entities.append(poster1)
 

    def _create_player(self):
        """Create the player character"""
        self.player = FirstPersonController(model='cube',color= color.orange, position=(-10, 1, 5), speed=8, collider='box')
        self.player.collider = BoxCollider(self.player, Vec3(0,1,0), Vec3(1,2,1))
        self.entities.append(self.player)
        
        # Reset camera to default state (important for scene transitions)
        camera.position = (0, 0, 0)
        camera.rotation = (0, 0, 0)
        camera.clip_plane_near = 0.1
        camera.clip_plane_far = 1000
        
        # Enable mouse lock
        mouse.locked = True
    
    def _create_interactive_objects(self):
        """Create interactive objects in the scene"""
        # Dummy props logic
        self.bed = Entity(model='assets/models/bed.glb', collider='box', scale=(2, 1.3 ,2), position=(-13, 0, 2.25), rotation=(0,-180,0))
        self.bed.tag = 'bed'
        self.entities.append(self.bed)
        
        self.sink = Entity(model='assets/models/metal_sink.glb', collider='box', scale=(3.2,3.2,3.2), position=(-4, 1.05, 0.67), rotation=(0,-180,0))
        self.sink.tag = 'sink'
        self.entities.append(self.sink)
        
        self.door = Entity(model='assets/models/prison_door.glb', collider='box', scale=1.5, position=(-2.5, 1.6, 5), rotation=(-180,-270,180))
        #self.door = Entity(model='assets/models/door_1.glb', collider='box', scale=1.0, position=(-8, 0, 9.4), texture='assets/textures/metal.jpg')
        self.door.tag = 'door'
        self.entities.append(self.door)
        
        #self.rejila = Entity(model='assets/models/grate.glb', scale=(0.3, 0.3, 0.3), position=(-9, 0.025, 1.2), texture='assets/textures/metal.jpg', collider='box')
        self.rejila = Entity(model='assets/models/grate.glb', scale=(0.3, 0.3, 0.3), position=(-13, 0.025, 2.25), texture='assets/textures/metal.jpg', collider='box')
        self.rejila.tag = 'vent'
        # Ventilation grate hinge to rotate like a lid
        self.rejila.origin = (-self.rejila.scale_x/2, 0, 0)
        self.entities.append(self.rejila)

        self.watch = Entity(model='assets/models/watch.glb', collider='box', scale=(1, 1, 1), position=(-6.2, 0, 2), rotation=(0, 0, 0))
        self.watch.tag = 'watch'
        self.entities.append(self.watch)

        self.poster2 = Entity(model='assets/models/poster_five.glb', collider='box', scale=(0.5, 0, 0.5), position=(-10, 0.2, 3), rotation=(0, 45, 0))
        self.poster2.tag = 'poster'
        self.entities.append(self.poster2)
    
    def _create_systems(self):
        """Create game systems"""
        # Create systems
        self.systems['ui'] = UIManager()
        self.systems['narrative'] = NarrativeManager()
        self.systems['state'] = GameState()
        self.systems['anim'] = AnimationSystem()
        
        # Add UI and animation elements to entities list for proper cleanup
        self.entities.append(self.systems['ui'].prompt)
        self.entities.append(self.systems['ui'].msg)
        self.entities.append(self.systems['ui'].banner)
        self.entities.append(self.systems['anim'].fade_overlay)
        
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
            inter=self.systems['inter'],
            scene=self
        )
        
        # Set the narrative system reference
        self.systems['controller'].narrative = self.systems['narrative']
        
        # Set up interaction system object references
        self.systems['inter'].bed = self.bed
        self.systems['inter'].sink = self.sink
        self.systems['inter'].vent = self.rejila
        self.systems['inter'].door = self.door
        self.systems['inter'].watch = self.watch
        self.systems['inter'].poster = self.poster2
    
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
    
    def _show_introduction(self):
        """Show the watcher's note introduction"""
        watcher_note = """
Prisoner, you have been assigned to Cell Block A.

Your objective is simple:
- Find the key hidden in this cell
- Something about the laundry room
- Something about the outside
- Do not attempt to escape through other means

Look carefully.

Good luck. You'll need it.

- W"""
        
        # Show the note with typewriter effect
        self.systems['narrative'].show_watcher_note(watcher_note)
    
    def update(self):
        """Update scene logic"""
        if not self.is_active:
            return
        
        try:
            if self.systems.get('controller'):
                self.systems['controller'].update()
        except:
            pass
    
    def input(self, key):
        """Handle input"""
        if not self.is_active:
            return
        
        try:
            if self.systems.get('controller'):
                self.systems['controller'].input(key)
        except:
            pass


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
        if self.prompt and hasattr(self.prompt, 'enabled'):
            try:
                self.prompt.text = text
                self.prompt.enabled = True
            except:
                pass
    
    def hide_prompt(self):
        if self.prompt and hasattr(self.prompt, 'enabled'):
            try:
                self.prompt.enabled = False
            except:
                pass

    def show_feedback(self, text, duration=1.2):
        if self.msg and hasattr(self.msg, 'enabled'):
            try:
                self.msg.text = text
                self.msg.enabled = True
                invoke(setattr, self.msg, 'enabled', False, delay=duration)
            except:
                pass
    
    def show_banner(self, text, duration=1.2):
        if self.banner and hasattr(self.banner, 'enabled'):
            try:
                self.banner.text = text
                self.banner.enabled = True
                invoke(setattr, self.banner, 'enabled', False, delay=duration)
            except:
                pass

class NarrativeManager:
    
    def __init__(self):
        self.note_overlay = None
        self.note_text = None
        self.is_showing_note = False
        self.typewriter_speed = 0.05  # seconds per character
        self.auto_dismiss_time = 15.0  # seconds
    
    def show_watcher_note(self, text, on_complete=None):
        if self.is_showing_note:
            return
        
        self.is_showing_note = True
        
        # Create note background (paper texture)
        self.note_overlay = Entity(
            parent=camera.ui,
            model='quad',
            color=color.rgb(245, 235, 200),  # Old paper color
            scale=(2, 2),
            z=-0.8
        )
        
        # Create note text
        self.note_text = Text(
            '',
            parent=camera.ui,
            origin=(0, 0),
            position=(0, 0),
            scale=1.5,
            color=color.black,
            font='VeraMono.ttf',
            z=-0.9
        )
        
        # Start typewriter effect
        self._typewriter_effect(text, on_complete)
    
    def _typewriter_effect(self, text, on_complete):
        current_text = ""
        char_index = 0
        
        def add_character():
            nonlocal current_text, char_index
            if char_index < len(text):
                current_text += text[char_index]
                self.note_text.text = current_text
                char_index += 1
                invoke(add_character, delay=self.typewriter_speed)
            else:
                # Typewriter complete, start auto-dismiss timer
                invoke(self._auto_dismiss, delay=self.auto_dismiss_time)
                if on_complete:
                    on_complete()
        
        # Start typewriter effect
        invoke(add_character, delay=0.5)  # Small delay before starting
    
    def _auto_dismiss(self):
        self.dismiss_note()
    
    def dismiss_note(self):
        # dim (si lo usás)
        if hasattr(self, 'dim') and self.dim:
            destroy(self.dim)          
            self.dim = None

        if self.note_overlay:
            destroy(self.note_overlay) 
            self.note_overlay = None

        if self.note_text:
            destroy(self.note_text)    
            self.note_text = None

        self.is_showing_note = False

        # callback de cierre si existe
        if getattr(self, '_on_close', None):
            self._on_close()
            self._on_close = None
    
    def handle_input(self, key):
        """Handle input for note interaction"""
        if self.is_showing_note and key:
            # Any key press dismisses the note
            self.dismiss_note()
            return True
        return False

class GameState:
    def __init__(self):
        self.has_key = False
        self.level_completed = False
        self.is_fading = False
        #
        self.injured = False
    
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
        self.msg_watch = ['Looks like a regular watch.', 'Hey, a watch!', 'It looks familiar...']
        self.msg_poster = ['It\'s a poster about science.', 'Why is this poster here?', 'Wow, my favorite game!']

        # entity hooks (assigned from outside)
        self.bed = None
        self.sink = None
        self.vent = None
        self.door = None
        self.watch = None
        self.poster = None

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

        # Safety check: ensure entities still exist and are valid
        try:
            ents = [e for e in (self.bed, self.sink, self.vent, self.door, self.watch, self.poster) 
                    if e is not None and hasattr(e, 'world_position')]
        except:
            self.ui.hide_prompt()
            return
        
        tgt = self._nearest(ents)
        self.current = tgt

        if not tgt:
            self.ui.hide_prompt()
            return

        tag = getattr(tgt, 'tag', None)
        if tag == 'bed':
            self.ui.show_prompt('E: Move the bed')
        elif tag == 'sink':
            self.ui.show_prompt('E: Inspect the sink')
        elif tag == 'vent':
            self.ui.show_prompt('E: Pry the grate')
        elif tag == 'door':
            self.ui.show_prompt('E: Try to open the door')
        elif tag == 'watch':
            self.ui.show_prompt('E: Inspect the watch')
        elif tag == 'poster':
            self.ui.show_prompt('E: Inspect the poster')
        else:
            self.ui.hide_prompt()

    def on_interact(self):
        """Call from input('e')."""
        if application.paused or self.state.is_fading or self.current is None:
            return

        tag = getattr(self.current, 'tag', None)

        if tag == 'bed':
            # Move the bed to reveal the grate
            self.ui.show_feedback('Moved the bed! I can see something underneath...')
            
            # Move bed instantly
            self.bed.position += Vec3(0, 0.1, -1.5)
            self.bed.rotation += Vec3(0, 15, 0)
            return

        if tag == 'sink':
            self.ui.show_feedback(random.choice(self.msg_sink))
            return

        if tag == 'vent':
            # lógica de la herida
            if not self.state.injured:
                self.state.injured = True
                self.ui.show_feedback('Ouch... I got injured!')
                try:
                    VFX.injury_flash()
                    VFX.spawn_blood_decal(self.player.position)
                except:
                    pass

            # lógica de la llave
            if not self.state.has_key:
                self.state.has_key = True
                self.ui.show_feedback('Got the key!')
                try:
                    self.vent.animate_rotation_z(-85, duration=.35, curve=curve.out_cubic)
                except:
                    pass
            else:
                self.ui.show_feedback('I already have the key.')
            return

        if tag == 'watch':
            self.ui.show_feedback(random.choice(self.msg_watch))
            return
        
        if tag == 'poster':
            self.ui.show_feedback(random.choice(self.msg_poster))
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

    def __init__(self, player, pause_handler, ui: UIManager, state: GameState, anim: AnimationSystem, inter: InteractionSystem, scene=None):
        GameController._inst = self
        self.player = player
        self.pause_handler = pause_handler
        self.ui = ui
        self.state = state
        self.anim = anim
        self.inter = inter
        self.scene = scene

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
        # update systems with safety checks
        try:
            if self.anim:
                self.anim.update()
        except:
            pass
        
        try:
            if self.inter:
                self.inter.update()
        except:
            pass
        
        try:
            VFX.update()
        except:
            pass
        
    def input(self, key):
        # Check if narrative is showing and handle input
        # primero deja que la narrativa consuma la tecla si está abierta
        if hasattr(self, 'narrative') and self.narrative and self.narrative.handle_input(key):
            return
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
        invoke(lambda: self.ui.show_banner('Door opened! You managed to escape the cell.', 1.1), delay=0.05)
        # 2) Banner "Level 1 completed"
        invoke(lambda: self.ui.show_banner('Level 1 completed!', 1.3), delay=1.20)
        # 3) Fade-out and transition to next level
        invoke(self._fade_and_transition, delay=2.60)
    
    def _fade_and_transition(self):
        """Fade to black and transition to intralevel"""
        self.anim.fade_to_black(duration=1.3, callback=self._transition_to_intralevel)
    
    def _transition_to_intralevel(self):
        """Transition from Level 1 to the intralevel (guard patrol scene)"""
        # Disable player
        if self.scene and hasattr(self.scene, 'player'):
            self.scene.player.enabled = False
            self.scene.player.gravity = 0
        
        mouse.locked = False
        
        # Transition to intralevel
        if self.scene and self.scene.scene_manager:
            self.scene.scene_manager.load_scene('intralevel')
        else:
            application.quit()

class VFX:
    overlay = Entity(parent=camera.ui, model='quad', color=color.rgba(255,0,0,0), scale=2, z=-0.88, enabled=True)
    t = 0.0
    dur = 1
    active = False

    @classmethod
    def injury_flash(cls):
        cls.t = 0.2
        cls.active = True
        cls.overlay.color = color.rgba(255,0,0,180)  # rojo semi
        Audio('assets/audio/ouch.wav', loop=False, autoplay=True, volume=8)

        # Texto grande en pantalla
        txt = Text('I HURT MYSELF!', origin=(0,0), scale=2, color=color.white, y=0.1, z=-0.9)
        # Lo eliminamos después de 1.2s
        invoke(destroy, txt, delay=1.2)

    @classmethod
    def update(cls):
        if not cls.active:
            return
        
        # Safety check: ensure overlay still exists
        if not cls.overlay or not hasattr(cls.overlay, 'color'):
            cls.active = False
            return
        
        try:
            cls.t += time.dt
            # Lerp de alpha a 0
            k = max(0.0, 1.0 - cls.t/cls.dur)
            a = int(180 * k)
            cls.overlay.color = color.rgba(255,0,0,a)
            if cls.t >= cls.dur:
                cls.overlay.color = color.rgba(255,0,0,0)
                cls.active = False
        except:
            cls.active = False
            
    @staticmethod
    def spawn_blood_decal(pos):
        for i in range(5):
            # Create blood decal with delay
            invoke(VFX._create_blood_decal, pos + Vec3(0, 0.01, 0), delay=i * 0.1)
    
    @staticmethod
    def _create_blood_decal(pos):
        """Create a single blood decal entity"""
        Entity(
            parent=scene,
            model='quad',
            texture='assets/textures/blood_decal.png',
            position=pos,
            rotation=(90,0,0),
            scale=2
        )
