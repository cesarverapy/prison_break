# ===== Imports base =====
from pathlib import Path
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import application
from panda3d.core import AntialiasAttrib
from .base_scene import BaseScene

# ================== Assets ==================
T_WALL = None
T_FLOOR = None
T_MATTRESS = None
T_FRAME = None
T_DOOR_PANEL = None
T_DOOR_FRAME = None

def _load_level2_assets():
    """Load level2 specific assets"""
    global T_WALL, T_FLOOR, T_MATTRESS, T_FRAME, T_DOOR_PANEL, T_DOOR_FRAME
    
    T_WALL = load_texture('assets/textures/walls.png')
    T_FLOOR = load_texture('assets/textures/floor_tile.png')
    T_MATTRESS = load_texture('assets/textures/mattress.png') if Path('assets/textures/mattress.png').exists() else None
    T_FRAME = load_texture('assets/textures/bed_frame.png') if Path('assets/textures/bed_frame.png').exists() else None
    T_DOOR_PANEL = load_texture('assets/textures/door_panel_metal.png') if Path('assets/textures/door_panel_metal.png').exists() else None
    T_DOOR_FRAME = load_texture('assets/textures/door_frame_metal.png') if Path('assets/textures/door_frame_metal.png').exists() else None


# ================== Constantes ==================
WALL_H     = 3.0
WALL_THICK = 0.20

# ================== Helpers ==================
def _setup_tex_repeat(tex):
    if not tex:
        return
    try:
        tex.wrap_mode = 'repeat'
        tex.filtering = 'mipmap'
        try:
            tex.set_anisotropy(16)
        except:
            pass
    except:
        pass

def make_wall(pos: Vec3, size: Vec3, repeat=(4, 1)):
    pos  = Vec3(round(pos.x, 3), round(pos.y, 3), round(pos.z, 3))
    size = Vec3(round(size.x, 3), round(size.y, 3), max(WALL_THICK, round(size.z, 3)))
    e = Entity(model='cube', texture=T_WALL, color=color.white,
               position=pos + Vec3(0, WALL_H / 2, 0),
               scale=size, collider='box')
    _setup_tex_repeat(e.texture)
    try:
        e.texture_scale = repeat
    except:
        pass
    return e

def make_floor(center: Vec3, w: float, d: float, repeat=(8, 4)):
    e = Entity(model='cube', position=center + Vec3(0, -0.03, 0),
               scale=Vec3(w, 0.06, d), texture=T_FLOOR, color=color.white, collider='box')
    _setup_tex_repeat(e.texture)
    try:
        e.texture_scale = repeat
    except:
        pass
    return e

def make_ceiling(center: Vec3, w: float, d: float, thickness: float = 0.06):
    """
    Techo sólido (slab) para evitar caras simples y z-fighting.
    Si existe textures/ceiling.png la usa; si no, color liso.
    """
    t = load_texture('textures/ceiling.png')
    e = Entity(
        model='cube',
        position=center + Vec3(0, WALL_H + thickness/2 + 0.02, 0),
        scale=Vec3(w, thickness, d),
        texture=t if t else None,
        color=(color.gray if t else color.rgb(220, 220, 220)),
        collider=None
    )
    _setup_tex_repeat(e.texture)
    try:
        e.texture_scale = (max(1, int(w/2)), max(1, int(d/2)))
    except:
        pass
    return e

# ---------- Curtain (with models if they exist, otherwise flat fallback) ----------
def make_curtain(x: float, z: float, w=1.8, rot_y: float = 0):
    for p in ('models/curtain.glb', 'models/curtain.gltf', 'models/curtain.obj'):
        try:
            curtain = Entity(model=p, position=Vec3(x, 0.0, z), rotation_y=rot_y, scale=1.0, collider='box')
            try:
                curtain.collider = BoxCollider(curtain, center=Vec3(0, 1.05, 0), size=Vec3(w, 2.1, 0.10))
            except:
                pass
            print('[MODEL] Cortina OK:', p)
            return curtain
        except Exception as e:
            print('[MODEL] Curtain failed', p, '->', e)

    tex = load_texture('textures/curtain.png')
    if not tex:
        return Entity(model='cube', color=color.rgb(60, 90, 150),
                      position=Vec3(x, 1.4, z), rotation_y=rot_y,
                      scale=Vec3(w, 2.2, 0.05), collider=None)
    e = Entity(model='cube', texture=tex, color=color.white,
               position=Vec3(x, 1.4, z), rotation_y=rot_y,
               scale=Vec3(w, 2.2, 0.05), collider=None)
    _setup_tex_repeat(tex)
    try:
        e.texture_scale = (w * 2, 1)
    except:
        pass
    Entity(parent=e, model='cube', color=color.rgb(40, 40, 40),
           position=Vec3(0, 1.15, 0), scale=Vec3(1.02, 0.05, 1.2))
    return e

# ---------- Decorados ----------
def spawn_wheelchair(pos: Vec3, rot_y: float = 45, scale: float = 1.0):
    try:
        e = Entity(model='models/wheelchair.glb', position=pos, rotation_y=rot_y, scale=scale, collider=None)
        print('[MODEL] Wheelchair OK')
        return e
    except Exception as e:
        print('[MODEL] Wheelchair fallback ->', e)

    root = Entity(position=pos, rotation_y=rot_y, collider=None)
    col_frame = color.rgb(70, 90, 120)
    col_wheel = color.rgb(35, 35, 35)
    col_seat  = color.rgb(55, 75, 95)

    r_big = 0.42 * scale; t_big = 0.06 * scale
    Entity(parent=root, model='cylinder', color=col_wheel,
           position=Vec3(-0.26*scale, r_big, -0.12*scale),
           rotation_x=90, scale=Vec3(r_big, r_big, t_big), collider=None)
    Entity(parent=root, model='cylinder', color=col_wheel,
           position=Vec3(+0.26*scale, r_big, -0.12*scale),
           rotation_x=90, scale=Vec3(r_big, r_big, t_big), collider=None)

    r_small = 0.13 * scale; t_small = 0.05 * scale
    Entity(parent=root, model='cylinder', color=col_wheel,
           position=Vec3(-0.18*scale, r_small*0.9, +0.22*scale),
           rotation_x=90, scale=Vec3(r_small, r_small, t_small), collider=None)
    Entity(parent=root, model='cylinder', color=col_wheel,
           position=Vec3(+0.18*scale, r_small*0.9, +0.22*scale),
           rotation_x=90, scale=Vec3(r_small, r_small, t_small), collider=None)

    Entity(parent=root, model='cube', color=col_seat,
           position=Vec3(0, 0.56*scale, -0.02*scale),
           scale=Vec3(0.52*scale, 0.05*scale, 0.46*scale), collider=None)
    Entity(parent=root, model='cube', color=col_seat,
           position=Vec3(0, 0.82*scale, -0.22*scale),
           scale=Vec3(0.52*scale, 0.50*scale, 0.05*scale), collider=None)

    for sx in (-1, 1):
        Entity(parent=root, model='cube', color=color.rgb(70,90,120),
               position=Vec3(0.22*sx*scale, 0.70*scale, -0.02*scale),
               scale=Vec3(0.04*scale, 0.06*scale, 0.48*scale), collider=None)
        Entity(parent=root, model='cube', color=color.rgb(70,90,120),
               position=Vec3(0.22*sx*scale, 0.52*scale, -0.02*scale),
               scale=Vec3(0.04*scale, 0.04*scale, 0.48*scale), collider=None)

    Entity(parent=root, model='cube', color=color.rgb(70,90,120),
           position=Vec3(0, 0.18*scale, 0.28*scale),
           scale=Vec3(0.52*scale, 0.02*scale, 0.18*scale), collider=None)
    return root

def spawn_table(pos: Vec3, rot_y: float = 0, scale: float = 1.0):
    for path in ('models/table.glb', 'models/table.obj'):
        try:
            print('[MODEL] Mesa OK:', path)
            return Entity(model=path, position=pos, rotation_y=rot_y, scale=scale, collider='box')
        except Exception as e:
            print('[MODEL] Table failed', path, '->', e)

    root = Entity(position=pos, rotation_y=rot_y, collider=None)
    col_top = color.rgb(170, 140, 100)
    col_leg = color.rgb(90, 90, 90)

    Entity(parent=root, model='cube', color=col_top,
           position=Vec3(0, 0.75*scale, 0),
           scale=Vec3(1.6*scale, 0.08*scale, 1.0*scale), collider='box')

    for sx in (-1, 1):
        for sz in (-1, 1):
            Entity(parent=root, model='cube', color=col_leg,
                   position=Vec3(0.7*sx*scale, 0.37*scale, 0.45*sz*scale),
                   scale=Vec3(0.08*scale, 0.75*scale, 0.08*scale))
    return root

def spawn_penguin(pos: Vec3, rot_y: float = 0, scale: float = 1.0):
    for path in ('models/penguin.glb', 'models/penguin.obj'):
        try:
            print('[MODEL] Penguin OK:', path)
            return Entity(model=path, position=pos, rotation_y=rot_y, scale=scale, collider=None)
        except Exception as e:
            print('[MODEL] Penguin failed', path, '->', e)

    p = Entity(position=pos, rotation_y=rot_y, collider=None)
    Entity(parent=p, model='sphere', color=color.rgb(30,30,30),
           scale=Vec3(0.5, 0.8, 0.5)*scale, y=0.4*scale)
    Entity(parent=p, model='sphere', color=color.white,
           scale=Vec3(0.35, 0.6, 0.45)*scale, y=0.4*scale, z=0.05*scale)
    Entity(parent=p, model='sphere', color=color.rgb(30,30,30),
           scale=Vec3(0.35, 0.35, 0.35)*scale, y=1.0*scale)
    Entity(parent=p, model='cone', color=color.rgb(250,180,60),
           scale=Vec3(0.10, 0.28, 0.10)*scale, position=Vec3(0, 0.95*scale, 0.25*scale), rotation_x=90)
    for sx in (-1, 1):
        Entity(parent=p, model='capsule', color=color.rgb(30,30,30),
               scale=Vec3(0.08, 0.40, 0.12)*scale, position=Vec3(0.28*sx*scale, 0.55*scale, 0),
               rotation_z=20*(-sx))
    for sx in (-1, 1):
        Entity(parent=p, model='cube', color=color.rgb(255,180,80),
               scale=Vec3(0.18, 0.04, 0.22)*scale, position=Vec3(0.10*sx*scale, 0.06*scale, 0.06*scale))
    return p

def distance_2d(a, b):
    ap = a if isinstance(a, Vec3) else a.position
    bp = b if isinstance(b, Vec3) else b.position
    return (Vec2(ap.x, ap.z) - Vec2(bp.x, bp.z)).length()

# ================== Base Interaction ==================
class Interactable(Entity):
    def __init__(self, prompt='Press E to interact', interact_distance=2.6, **kwargs):
        kwargs.setdefault('collider', 'box')
        super().__init__(**kwargs)
        self.prompt = prompt
        self.interact_distance = interact_distance
        self.enabled = True
    def can_interact(self, who) -> bool:
        return self.enabled and distance_2d(self, who) <= self.interact_distance
    def on_interact(self, game): pass

# ================== Items ==================
class ItemPickup(Interactable):
    MODEL_CFG = {
        'gloves':    {'type': 'single', 'model': 'models/gloves.glb',  'y': 0.125, 'scale': 0.21, 'rot_y':  15},
        'bandages':  {'type': 'single', 'model': 'models/band.glb',    'y': 0.110, 'scale': 0.01, 'rot_y': -10},
        'tourniquet':{'type': 'single', 'model': 'models/blood.glb',   'y': 0.050, 'scale': 1.0,  'rot_y':   0},
        'syringe':   {'type': 'parts',  'parts': [
            'models/syringe_body.obj',
            'models/syringe_plunger.obj',
            'models/syringe_needle.obj'
        ], 'y': 0.10, 'scale': 1.0, 'rot_y': 30},
    }
    def __init__(self, item_id, **kwargs):
        super().__init__(prompt='Press E to pick up', **kwargs)
        self.item_id = item_id
        self.visible = True
        self.collider = BoxCollider(self, center=Vec3(0, 0.15, 0), size=Vec3(0.6, 0.35, 0.6))
        self._spawn_visual_for_item(item_id)
    def _spawn_visual_for_item(self, item_id: str):
        name = item_id.lower()
        cfg = self.MODEL_CFG.get(name)
        try:
            if cfg and cfg['type'] == 'single':
                e = Entity(parent=self, model=cfg['model'], y=cfg.get('y', 0.12), scale=cfg.get('scale', 1.0))
                e.rotation_y = cfg.get('rot_y', 0)
            elif cfg and cfg['type'] == 'parts':
                group = Entity(parent=self, y=cfg.get('y', 0.1), scale=cfg.get('scale', 1.0))
                for m in cfg['parts']:
                    Entity(parent=group, model=m)
                group.rotation_y = cfg.get('rot_y', 0)
            else:
                raise FileNotFoundError('No model config found.')
        except Exception as ex:
            print(f'[INFO] Model not loaded for "{item_id}" -> using cube fallback. Detail: {ex}')
            vis = Entity(parent=self, model='cube', y=0.13, scale=Vec3(0.35, 0.25, 0.35),
                         texture=T_WALL, color=color.white)
            _setup_tex_repeat(vis.texture)
    def on_interact(self, game):
        if not self.enabled: return
        self.enabled = False
        self.visible = False
        try: Audio('audio/collect.wav').play()
        except: pass
        game.collect_item(self.item_id)

# ---------- SINK (interactable) ----------
class Sink(Interactable):
    def __init__(self, **kwargs):
        super().__init__(prompt='Press E to WASH YOUR HANDS', interact_distance=2.6, **kwargs)
        # Intentar modelo 3D
        for p in ('models/sink.glb', 'models/sink.gltf', 'models/sink.obj'):
            try:
                Entity(parent=self, model=p, collider=None, scale=1.0)
                break
            except Exception as e:
                print('[MODEL] Sink failed', p, '->', e)
        else:
            # Fallback geométrico: base + pileta + canilla
            base_w, base_d, base_h = 0.60, 0.42, 0.80
            Entity(parent=self, model='cube', color=color.rgb(215,215,215),
                   position=Vec3(0, base_h/2, 0), scale=Vec3(base_w, base_h, base_d))
            # Pileta
            Entity(parent=self, model='cube', color=color.rgb(240,240,240),
                   position=Vec3(0, base_h + 0.04, 0), scale=Vec3(base_w*0.98, 0.08, base_d*0.98))
            # Canilla
            Entity(parent=self, model='cylinder', color=color.rgb(180,180,180),
                   position=Vec3(0, base_h + 0.16, base_d*0.10), rotation_x=90, scale=Vec3(0.03, 0.03, 0.10))
        # Collider general (cajón)
        try:
            BoxCollider(self, center=Vec3(0, 0.45, 0.0), size=Vec3(0.7, 0.9, 0.5))
        except:
            pass

    def on_interact(self, game):
        try: Audio('audio/water.wav').play()
        except: pass
        print('[SINK] You washed your hands')

# Helper: place sink "attached" to a wall with slight offset and correct rotation
def spawn_sink_on_wall(anchor: Vec3, facing: str = '+Z', height: float = 0.0, offset: float = 0.06) -> Sink:
    """
    anchor: point on the wall (x, y, z). Normally y=0 and height controls the elevation.
    facing: '+Z', '-Z', '+X', '-X' (direction the sink faces).
    height: height of origin (0=floor). The sink centers its base according to the model; 0.0 works well.
    offset: separation so it doesn't clip into the wall.
    """
    facing = facing.upper()
    rot_map = {'+Z':   0, '-Z': 180, '+X':  90, '-X': -90}
    nrm_map = {'+Z': Vec3(0,0, 1), '-Z': Vec3(0,0,-1), '+X': Vec3( 1,0,0), '-X': Vec3(-1,0,0)}
    ry = rot_map.get(facing, 0)
    n  = nrm_map.get(facing, Vec3(0,0,1))

    pos = Vec3(anchor.x, height, anchor.z) + n * offset
    return Sink(position=pos, rotation_y=ry)

def spawn_reji(pos: Vec3, rot_y: float = 0,
               size=(0.30, 0.38), on_floor: bool = True, name: str = 'reji',
               scale_model: float = 0.06, force_fallback: bool = False,
               use_cube: bool = False, thickness: float = 0.02, lift: float = 0.01):
    # normalize size
    if isinstance(size, (list, tuple)) and len(size) >= 2:
        w, d = float(size[0]), float(size[1])
        if len(size) >= 3: thickness = float(size[2])
    else:
        w, d = 0.30, 0.38

    # --- TRY 3D MODEL ---
    if not force_fallback:
        for p in ('models/reji.glb','models/reji.gltf','models/reji.obj',
                  'models/grate.glb','models/grate.gltf','models/grate.obj'):
            try:
                root = Entity(name=name, position=pos, rotation_y=rot_y)       # wrapper
                mesh = Entity(parent=root, model=p, collider=None, scale=scale_model)
                print('[GRATE] Using 3D model with scale=', scale_model)

                if on_floor:
                    # Align the bottom of the model to the floor (y = pos.y + lift)
                    try:
                        mn, mx = mesh.get_tight_bounds()        # world coords (Point3)
                        desired_y = pos.y + lift
                        mesh.y += (desired_y - mn.y)            # raise/lower child until it rests
                    except Exception as e:
                        print('[REJI] bounds fail:', e)
                        mesh.y = lift
                return root
            except Exception as ex:
                print('[MODEL] Grate failed', p, '->', ex)

    # --- FALLBACK (flat panel or thin plate) ---
    tex = load_texture('textures/reji.png') or load_texture('textures/grate.png')
    y = pos.y + (lift if on_floor else 0.0)

    if use_cube:
        e = Entity(name=name, model='cube',
                   texture=tex if tex else None,
                   color=color.white if tex else color.rgb(150,150,150),
                   position=Vec3(pos.x, y, pos.z),
                   rotation_x=(90 if on_floor else 0),
                   rotation_y=rot_y,
                   scale=Vec3(w, thickness, d),
                   unlit=True, collider=None)
    else:
        e = Entity(name=name, model='quad',
                   texture=tex if tex else None,
                   color=color.white if tex else color.rgb(150,150,150),
                   position=Vec3(pos.x, y, pos.z),
                   rotation_x=(90 if on_floor else 0),
                   rotation_y=rot_y,
                   scale=Vec3(w, d, 1),
                   unlit=True, collider=None)

    try:
        if tex and '_setup_tex_repeat' in globals():
            _setup_tex_repeat(e.texture)
            e.texture_scale = (max(1, int(w*4)), max(1, int(d*4)))
    except: pass

    return e



# ================== Puerta corrediza (embellecida) ==================
class SlidingDoor(Interactable):
    def __init__(self, width=1.2, theme='exit', label_text='SALIDA', speed=2.8, **kwargs):
        super().__init__(prompt='Puerta', **kwargs)
        self.collider = None
        self.width, self.speed = width, speed
        self._open = False

        if theme == 'exit':
            panel_col = color.rgb(70, 165, 115)
            frame_col = color.rgb(45, 45, 50)
            glass_tint = color.rgba(160, 200, 220, 120)
            handle_col = color.rgb(220, 220, 220)
        else:
            panel_col = color.rgb(230, 230, 235)
            frame_col = color.rgb(55, 55, 60)
            glass_tint = color.rgba(175, 205, 225, 120)
            handle_col = color.rgb(200, 200, 200)

        self.frame = Entity(parent=self)
        jamb_w, header_h, depth = 0.18, 0.16, 0.12
        for sx in (-1, 1):
            Entity(parent=self.frame, model='cube',
                   texture=T_DOOR_FRAME, color=(color.gray if T_DOOR_FRAME else frame_col),
                   position=Vec3(sx*(width/2 + jamb_w/2), WALL_H/2, 0),
                   scale=Vec3(jamb_w, WALL_H, depth+0.05))
        Entity(parent=self.frame, model='cube',
               texture=T_DOOR_FRAME, color=(color.white if T_DOOR_FRAME else frame_col),
               position=Vec3(0, 2.45, 0), scale=Vec3(width + jamb_w*2, header_h, depth+0.04))
        Entity(parent=self.frame, model='cube', color=frame_col,
               position=Vec3(0, 2.52, depth/2 + 0.04), scale=Vec3(width + 0.2, 0.05, 0.02))

        ph = 2.28
        panel_depth = depth
        self.panel_left  = Entity(parent=self.frame, model='cube',
                                  texture=T_DOOR_PANEL, color=(color.white if T_DOOR_PANEL else panel_col),
                                  collider='box', position=Vec3(-width/4, 1.15, 0),
                                  scale=Vec3(width/2, ph, panel_depth))
        self.panel_right = Entity(parent=self.frame, model='cube',
                                  texture=T_DOOR_PANEL, color=(color.white if T_DOOR_PANEL else panel_col),
                                  collider='box', position=Vec3(+width/4, 1.15, 0),
                                  scale=Vec3(width/2, ph, panel_depth))
        for p in (self.panel_left.texture, self.panel_right.texture):
            _setup_tex_repeat(p)
        try:
            self.panel_left.texture_scale = (1, 1.2)
            self.panel_right.texture_scale = (1, 1.2)
        except:
            pass

        win_w, win_h, win_off_y = 0.48, 0.32, 0.36
        for panel in (self.panel_left, self.panel_right):
            Entity(parent=panel, model='cube', color=color.rgb(30,30,30),
                   position=Vec3(0, win_off_y, panel_depth/2 - 0.02), scale=Vec3(win_w+0.02, win_h+0.02, 0.015))
            Entity(parent=panel, model='quad', color=glass_tint,
                   position=Vec3(0, win_off_y, panel_depth/2 + 0.001), scale=Vec2(win_w, win_h))

        handle_h, handle_x_off = 0.78, (width/2)*0.40
        for xoff in (+handle_x_off, -handle_x_off):
            Entity(parent=self.panel_left  if xoff>0 else self.panel_right,
                   model='cube', color=handle_col,
                   position=Vec3(xoff, 1.05, panel_depth/2 + 0.015),
                   scale=Vec3(0.03, handle_h, 0.02))

        if label_text:
            bg = Entity(parent=self.frame, model='cube',
                        texture=T_DOOR_FRAME, color=(color.white if T_DOOR_FRAME else frame_col),
                        position=Vec3(0, 2.64, panel_depth/2 + 0.025), scale=Vec3(0.86, 0.16, 0.02))
            Text(parent=bg, text=label_text, origin=(0, 0), world_scale=0.7, y=-0.015, x=-0.22, color=color.white)

    def open(self, slide=1.22, duration=0.7):
        if self._open: return
        self._open = True
        self.enabled = False
        self.panel_left.animate_x (self.panel_left.x  - slide, duration=duration, curve=curve.out_sine)
        self.panel_right.animate_x(self.panel_right.x + slide, duration=duration, curve=curve.out_sine)
        invoke(setattr, self.panel_left,  'collider', None, delay=duration+0.05)
        invoke(setattr, self.panel_right, 'collider', None, delay=duration+0.05)
        try: Audio('audio/door_slide.wav').play()
        except: pass

# ================== Pared Rompible ==================
class BreakableWall(Interactable):
    def __init__(self, size: Vec3, **kwargs):
        super().__init__(prompt='(Bloqueada por ahora)', **kwargs)
        self.size = size
        self._broken = False
        self.visual = Entity(parent=self, model='cube', texture=T_WALL, color=color.white,
                             position=Vec3(0, WALL_H/2, 0), scale=size, collider=None)
        _setup_tex_repeat(self.visual.texture)
        self.collider = BoxCollider(self, center=Vec3(0, WALL_H/2, 0), size=size + Vec3(0.02,0.02,0.02))
    def break_now(self):
        if self._broken: return
        self._broken = True
        self.enabled = False
        self.collider = None
        self.visual.animate_color(color.rgba(255,255,255,30), duration=0.25)
        self.visual.animate_scale(self.size * Vec3(1.00, 0.10, 1.00), duration=0.18)
        try: Audio('audio/impact.wav').play()
        except: pass



# ================== Level 2 Scene ==================
class Level2Scene(BaseScene):
    """Level 2: Medical Bay - Apply tourniquet and escape"""
    
    def __init__(self, scene_manager=None):
        super().__init__()
        self.scene_manager = scene_manager
        self.player = None
        self.exit_door = None
        self.return_door = None  # Door to go back to intralevel
        self.is_transitioning = False
        self.interact_distance = 2.6
    
    def setup(self):
        """Initialize Level 2 scene"""
        self.is_active = True
        
        # Load assets
        _load_level2_assets()
        
        # Create environment and game elements
        self._setup_game()
    
    def _setup_game(self):
        """Set up all game elements"""
        # Pasillo principal
        floor1 = make_floor(Vec3(12, 0, 3), 24, 6, repeat=(8, 4))
        ceiling1 = make_ceiling(Vec3(12, 0, 3), 24, 6)
        wheelchair = spawn_wheelchair(Vec3(22.8, 0.9, 1.6), rot_y=20, scale=0.8)
        penguin = spawn_penguin(Vec3(22.8, 0.9, 1.6), rot_y=60, scale=0.3)
        sink = spawn_sink_on_wall(Vec3(7.0, 1.5, 1.70), facing='-Z', height=0.8, offset=0.07)
        
        self.entities.extend([floor1, ceiling1, wheelchair, penguin, sink])

        # Perímetro superior e inferior
        wall1 = make_wall(Vec3(12.0, 0, 0.0), Vec3(24.0, WALL_H, WALL_THICK))
        wall2 = make_wall(Vec3(12.0, 0, 6.0), Vec3(24.0, WALL_H, WALL_THICK))
        self.entities.extend([wall1, wall2])

        self.rejis = [
            spawn_reji(Vec3(6.0, 0.0, 2.3),  rot_y=0,  on_floor=True,  name='reji', scale_model=0.0018),
            spawn_reji(Vec3(12.0, 0.0, 3.7), rot_y=90, on_floor=True,  name='reji', scale_model=0.0029),
        ]
        self.entities.extend(self.rejis)

        reji_wall = spawn_reji(Vec3(24.0, 1.2, 3.0), rot_y=90, size=(0.16, 0.16), on_floor=False, name='reji', scale_model=0.008)
        self.entities.append(reji_wall)

        # Perímetro derecho (x=24)
        wall3 = make_wall(Vec3(24.0, 0, 3.0), Vec3(WALL_THICK, WALL_H, 6.0))
        self.entities.append(wall3)

        # Perímetro izquierdo (x=0) con hueco central para salida (1.2 m)
        door_width = 1.2
        wall4 = make_wall(Vec3(0.0, 0, 1.2), Vec3(WALL_THICK, WALL_H, 2.4))
        wall5 = make_wall(Vec3(0.0, 0, 4.8), Vec3(WALL_THICK, WALL_H, 2.4))
        self.entities.extend([wall4, wall5])
        
        self.exit_wall = BreakableWall(size=Vec3(WALL_THICK, WALL_H, door_width),
                                       position=Vec3(0.0, 0.0, 3.0))
        self.entities.append(self.exit_wall)

        # Cubículos (posiciones + rotación de camas)
        BEDS = [
            (Vec3(5.0,  0.09, 2),  90),
            (Vec3(9.0,  0.09, 2), -90),
            (Vec3(13.0, 0.09, 2), 180),
        ]
        for pos, rot in BEDS:
            wall = make_wall(Vec3(pos.x, 0, 0.7), Vec3(3.6, WALL_H, WALL_THICK))
            bed = self._make_bed(pos, rot_y=rot)
            self.entities.extend([wall, bed])

        # Oficina
        office_x = 19.0
        floor2 = make_floor(Vec3(office_x, 0, 1.0), 4.0, 6.0)
        ceiling2 = make_ceiling(Vec3(office_x, 0, 1.0), 4.0, 6.0)
        wall6 = make_wall(Vec3(office_x, 0, -2.0), Vec3(4.0, WALL_H, WALL_THICK))
        wall7 = make_wall(Vec3(office_x - 2.0, 0, 1.2), Vec3(WALL_THICK, WALL_H, 2.4))
        wall8 = make_wall(Vec3(office_x - 2.0, 0, 4.8), Vec3(WALL_THICK, WALL_H, 2.4))
        wall9 = make_wall(Vec3(office_x + 2.0, 0, 0.6), Vec3(WALL_THICK, WALL_H, 6.0))
        self.entities.extend([floor2, ceiling2, wall6, wall7, wall8, wall9])

        self.office_door = SlidingDoor(
            position=Vec3(office_x - 2.0, 0, 3.0),
            width=1.2, theme='office', label_text='OFFICE', rotation_y=90
        )
        self.entities.append(self.office_door)

        # Required items
        self.items_needed = {'Gloves', 'Syringe', 'Bandages'}
        self.items_collected = set()
        item1 = ItemPickup('Gloves', position=Vec3(7.3, 0.1, 4.6))
        item2 = ItemPickup('Syringe', position=Vec3(1.7, 0.1, 0.6))
        item3 = ItemPickup('Bandages', position=Vec3(13.2, 0.1, 2.6))
        self.entities.extend([item1, item2, item3])

        # Tourniquet station
        self.tourniquet_station = Interactable(
            prompt='Press E to apply tourniquet',
            position=Vec3(office_x, 1.2, 2.0),
            collider='box'
        )
        table = spawn_table(Vec3(office_x, 0.091, 2.0), rot_y=90, scale=1.1)
        blood_model = Entity(parent=self.tourniquet_station, model='assets/models/blood.glb', y=0.01, scale=1.0, rotation_y=0)
        self.tourniquet_station.collider = BoxCollider(self.tourniquet_station,
                                                       center=Vec3(0, 0.15, 0), size=Vec3(0.9, 0.3, 0.9))
        self.entities.extend([self.tourniquet_station, table])
        self.tourniquet_done = False

        # ADD RETURN DOOR to intralevel (at entrance)
        self.return_door = SlidingDoor(
            position=Vec3(24.0, 0, 3.0),
            width=1.2, theme='exit', label_text='RETURN', rotation_y=-90
        )
        self.return_door.tag = 'return_door'
        self.entities.append(self.return_door)

        # Player - spawn INSIDE the medical bay (past the entrance door)
        self.player = FirstPersonController(position=Vec3(10.0, 1.2, 3), speed=5, jump_height=0.55)
        self.player.collider = BoxCollider(self.player, center=Vec3(0, 1, 0), size=Vec3(0.6, 1.9, 0.6))
        self.player.rotation_y = -90  # Face toward the main hallway (away from entrance door)
        self.player.gravity = 1
        self.player.enabled = True
        self.entities.append(self.player)

        # Reset camera to default state
        camera.position = (0, 0, 0)
        camera.rotation = (0, 0, 0)
        camera.clip_plane_near = 0.1
        camera.clip_plane_far = 1000
        
        # Enable mouse lock for FPS control
        mouse.locked = True
        
        try:
            application.base.render.setAntialias(AntialiasAttrib.MMultisample)
        except:
            pass

        # HUD
        window.title = 'Medical Bay - Apply tourniquet and escape'
        window.color = color.rgb(10, 10, 10)
        self.hud_text = Text(text='', origin=(-.5, .5), x=-.87, y=.45, scale=1)
        self.timer_text = Text(text='', origin=(.5, .5), x=.85, y=.45, scale=1)
        self.prompt_text = Text(text='', origin=(0, -.5), y=-.42, scale=1)
        self.entities.extend([self.hud_text, self.timer_text, self.prompt_text])

        # Fade overlay for transitions
        self.fade_overlay = Entity(
            parent=camera.ui,
            model='quad',
            color=color.rgba(0, 0, 0, 255),  # Start black
            scale=2,
            z=-0.9,
            enabled=True
        )
        self.entities.append(self.fade_overlay)
        
        # Fade in from black at start
        self.fade_overlay.animate_color(color.rgba(0, 0, 0, 0), duration=1.0, curve=curve.in_out_sine)

        self.time_left = 30.0
        self.game_over = False
        self.victory = False
        self._pressing_e = False
        self._center_text = None
        
        self.update_hud()

    # --------- Bed (uses model if exists; otherwise, cubic fallback) ---------
    def _make_bed(self, pos: Vec3, rot_y: float = 0):
        """Creates a bed at pos with Y rotation (degrees)."""
        root = Entity(position=pos, rotation_y=rot_y,scale=0.012)  # wrapper to rotate/position everything

        # Try models
        for p in ('models/hospital_bed.glb', 'models/hospital_bed.gltf', 'models/hospital_bed.obj'):
            try:
                Entity(parent=root, model=p, collider='box')
                try:
                    BoxCollider(root, center=Vec3(0, 0.30, 0), size=Vec3(2.0, 0.6, 0.9))
                except:
                    pass
                print('[MODEL] Bed OK:', p)
                return root
            except Exception as e:
                print('[MODEL] Bed failed', p, '->', e)

        # Cubic fallback
        bed_len, bed_w, base_h, mat_h = 2.0, 0.9, 0.18, 0.22
        Entity(parent=root, model='cube', texture=T_FRAME if T_FRAME else None,
               color=(color.white if T_FRAME else color.rgb(160,160,165)),
               position=Vec3(0, base_h/2 - 0.01, 0),
               scale=Vec3(bed_len, base_h, bed_w), collider='box')
        Entity(parent=root, model='cube', texture=T_MATTRESS if T_MATTRESS else None,
               color=(color.white if T_MATTRESS else color.rgb(230,230,235)),
               position=Vec3(0, base_h + mat_h/2 - 0.01, 0),
               scale=Vec3(bed_len*0.98, mat_h, bed_w*0.98))
        return root

    # --------- HUD / Logic ---------
    def update_hud(self):
        missing = self.items_needed - self.items_collected
        got = len(self.items_collected)
        self.hud_text.text = (
            f"Required: {', '.join(self.items_needed)} | You have: {got}/3 | Missing: {', '.join(missing)}"
            if missing else f"Objective complete - You have: {', '.join(self.items_collected)}"
        )
        if not missing and not self.office_door._open:
            self.office_door.open()

    def collect_item(self, item_id):
        self.items_collected.add(item_id)
        self.update_hud()

    def _unlock_exit_wall(self):
        if self.exit_door:
            return
        if self.exit_wall:
            self.exit_wall.break_now()
        self.exit_door = SlidingDoor(position=Vec3(0.0, 0.0, 3.0), width=1.2, theme='exit', label_text='EXIT')
        self.exit_door.open()

    def _apply_tourniquet(self):
        missing = self.items_needed - self.items_collected
        if missing:
            self.prompt_text.text = f"Missing: {', '.join(missing)}"
            return
        self.tourniquet_done = True
        try: Audio('audio/success.wav').play()
        except: pass
        self.hud_text.text = '✔ Tourniquet applied — EXIT UNLOCKED!'
        self.prompt_text.text = 'Head to the EXIT'
        self._unlock_exit_wall()

    def _end(self, message: str, win: bool):
        """End game with message"""
        self.game_over = not win
        self.victory = win
        
        if self.player:
            self.player.enabled = False
        
        if self._center_text:
            destroy(self._center_text)
        
        self._center_text = Text(
            text=message, origin=(0,0), scale=2,
            color=color.green if win else color.red, background=True
        )
        invoke(application.quit, delay=2)

    def update(self):
        """Update scene logic"""
        if not self.is_active:
            return
        
        if self.game_over or self.victory or self.is_transitioning:
            return

        # Timer
        self.time_left = max(0.0, self.time_left - time.dt)
        self.timer_text.text = f'Time: {int(self.time_left + 0.99)}s'
        if self.time_left <= 0 and not self.tourniquet_done:
            self.prompt_text.text = 'You bled out... GAME OVER'
            self.hud_text.text = 'Restarting...'
            self._end('GAME OVER', win=False)
            return

        # Check proximity to return door
        if self.return_door and self.player:
            dist = distance_2d(self.player.position, self.return_door.position)
            if dist <= self.interact_distance:
                self.prompt_text.text = 'Press E to return to prison area'
                return  # Don't check other interactions

        # Interactions
        target = next((e for e in self.entities if isinstance(e, Interactable) and e.can_interact(self.player)), None)
        self.prompt_text.text = (target.prompt if target else '')
        e_down = held_keys.get('e', False)
        if target and e_down and not getattr(self, '_pressing_e', False):
            self._pressing_e = True
            if target is self.tourniquet_station:
                self._apply_tourniquet()
            else:
                target.on_interact(self)
        elif not e_down:
            self._pressing_e = False

        # Victory: cross the exit
        if self.tourniquet_done and self.player.x < 0.6:
            self._end('LEVEL COMPLETED!', win=True)
    
    def input(self, key):
        """Handle input"""
        if not self.is_active:
            return
        
        # Return to intralevel
        if key == 'e' and not self.is_transitioning and self.return_door and self.player:
            dist = distance_2d(self.player.position, self.return_door.position)
            if dist <= self.interact_distance:
                self._return_to_intralevel()
    
    def _return_to_intralevel(self):
        """Transition back to intralevel scene"""
        if self.is_transitioning:
            return
        
        self.is_transitioning = True
        self.prompt_text.enabled = False
        
        if self.player:
            self.player.enabled = False
        mouse.locked = False
        
        try:
            Audio('assets/audio/door_slide.wav', loop=False, autoplay=True)
        except:
            pass
        
        self._fade_to_black(duration=1.0, callback=self._transition_to_intralevel_scene)
    
    def _fade_to_black(self, duration=1.0, callback=None):
        """Fade screen to black"""
        if not self.fade_overlay:
            if callback:
                callback()
            return
        
        self.fade_overlay.animate_color(color.rgba(0, 0, 0, 255), duration=duration, curve=curve.in_out_sine)
        if callback:
            invoke(callback, delay=duration)
    
    def _transition_to_intralevel_scene(self):
        """Transition to intralevel scene"""
        if self.player:
            self.player.enabled = False
            self.player.gravity = 0
        
        mouse.locked = False
        self.scene_manager.load_scene('intralevel', spawn_at_medical_bay=True)
    
    def cleanup(self):
        """Clean up scene resources"""
        if self.player:
            self.player.enabled = False
        super().cleanup()
