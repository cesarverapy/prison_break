# Simple Prison Map - Just the essentials + Keypad 731 + Portal + Fade + UI final legible (sin 'capsule')
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import math

app = Ursina()
Sky()

# ==========================
# BASIC SETUP
# ==========================
window.fullscreen = True
window.color = color.rgb(0, 0, 0)

# ==========================
# PLAYER
# ==========================
player = FirstPersonController(y=3, speed=5)
player.cursor.visible = True
player.gravity = 0.5

# ==========================
# GROUND
# ==========================
ground = Entity(model='plane', scale=(60, 1, 60), collider='mesh',
                color=color.rgb(0, 0, 0), unlit=True)

# ==========================
# FENCE
# ==========================
def create_fence():
    for x in range(-20, 21, 4):
        Entity(model='cube', position=(x, 3, -20), scale=(0.2, 6, 0.2),
               color=color.rgb(169, 169, 169), collider='box', unlit=True)
        Entity(model='cube', position=(x, 3, 20), scale=(0.2, 6, 0.2),
               color=color.rgb(169, 169, 169), collider='box', unlit=True)
    for z in range(-20, 21, 4):
        Entity(model='cube', position=(-20, 3, z), scale=(0.2, 6, 0.2),
               color=color.rgb(169, 169, 169), collider='box', unlit=True)
        Entity(model='cube', position=(20, 3, z), scale=(0.2, 6, 0.2),
               color=color.rgb(139, 69, 19), collider='box', unlit=True)
create_fence()

# ==========================
# TOWERS
# ==========================
for pos in [(-20, 20), (20, 20), (-20, -20), (20, -20)]:
    Entity(model='assets/models/guard_tower.glb', position=(pos[0], 0, pos[1]), scale=(5, 16, 5), collider='box', texture='brick')

# ==========================
# COURT
# ==========================
Entity(model='cube', position=(0, 0.15, 0), scale=(18, 0.3, 10),
       color=color.rgb(169, 169, 169), collider='box', unlit=True)

# ==========================
# BENCHES
# ==========================
for bx in (-7, -4, 4, 7):
    Entity(model='cube', position=(bx, 0.4, 3), scale=(2.5, 0.8, 0.6),
           color=color.rgb(160, 82, 45), collider='box', unlit=True)

# ==========================
# INTERACTIVE ELEMENTS
# ==========================
pista_obj = Entity(model='cube', position=(-5, 1.2, -10), scale=(1.8, 1.2, 0.3),
                   color=color.azure, collider='box', unlit=True)
Text("PISTA (E)", world_scale=1.4, position=pista_obj.position + Vec3(-1.1, 1.0, 0.2), color=color.cyan)

panel_colores = Entity(model='cube', position=(5, 1.2, -10), scale=(1.8, 1.2, 0.3),
                       color=color.rgb(169, 169, 169), collider='box', unlit=True)
Text("COLORES (E)", world_scale=1.2, position=panel_colores.position + Vec3(-1.2, 1.0, 0.2), color=color.cyan)

keypad = Entity(model='cube', position=(-3, 1.2, 19), scale=(1.1, 1.2, 0.3),
                color=color.rgb(0, 0, 255), collider='box', unlit=True)
Text("KEYPAD (E)", world_scale=1.5, position=keypad.position + Vec3(-1.2, 1.1, 0.2), color=color.cyan)

# Simón (visual, no requerido)
simon = Entity(model='cube', position=(15, 1.2, 1.5), scale=(1, 1.2, 0.3),
               color=color.rgb(0, 255, 0), collider='box', unlit=True)
Text("SIMÓN (E)", world_scale=1.3, position=simon.position + Vec3(-1, 1.1, 0.2), color=color.cyan)

# Puerta
door = Entity(model='cube', position=(0, 2, 25), scale=(4, 4, 0.2),
              color=color.rgb(139, 69, 19), collider='box', unlit=True)

# Trigger lógico detrás de la puerta
door_trigger = Entity(position=(0, 1.5, 26.5), scale=(4.2, 4.0, 2.5),
                      collider='box', visible=False)

# ==========================
# HUD
# ==========================
objective_text = Text("Objetivo: Resuelve los acertijos para abrir la puerta. (R = Reset)",
                      parent=camera.ui, position=Vec2(0, .44), origin=(0, 0), scale=1.25, background=True)
prompt_text = Text("", parent=camera.ui, position=Vec2(0, -.42), origin=(0, 0), scale=1.45, background=True)
def show_prompt(msg, t=2):
    prompt_text.text = msg
    invoke(lambda: setattr(prompt_text, 'text', ''), delay=t)

# ==========================
# ESTADO / VARS
# ==========================
keypad_correct = ['7','3','1']
keypad_input = []
keypad_ok = False
door_opened = False
end_scene_started = False

portal = None
portal_trigger = None
_portal_phase = 0.0

# Fade overlay: ponerlo BIEN arriba (más negativo = más cerca en UI)
fade_overlay = Entity(parent=camera.ui, model='quad',
                      color=color.rgba(0, 0, 0, 0), scale=(2, 2), z=-0.9)
fade_overlay.visible = True

def fade_to_black_then(callback, t_in=0.6, t_out=0.6, hold=0.1):
    fade_overlay.animate_color(color.rgba(0, 0, 0, 255), duration=t_in, curve=curve.linear)
    invoke(lambda: (callback(),
                    fade_overlay.animate_color(color.rgba(0,0,0,0), duration=t_out, curve=curve.linear)),
           delay=t_in + hold)

# ==========================
# HELPERS
# ==========================
def get_interactable():
    hit = raycast(camera.world_position, camera.forward, distance=4.0, ignore=(player,))
    return hit.entity if hit.hit else None

def lock_player(lock: bool):
    mouse.locked = not lock
    player.enabled = not lock
    player.cursor.visible = lock

# ==========================
# UI KEYPAD
# ==========================
keypad_ui = None
def destroy_ui():
    global keypad_ui
    if keypad_ui:
        destroy(keypad_ui); keypad_ui = None
    lock_player(False)

def create_keypad_ui():
    global keypad_ui, keypad_input, keypad_ok
    if keypad_ui: return
    keypad_input = []
    lock_player(True)

    keypad_ui = Entity(parent=camera.ui)
    Panel(parent=keypad_ui, scale=(.45,.6), color=color.rgba(0, 0, 0, 200), z=-.2, texture='white_cube')
    display = Text(parent=keypad_ui, text="_", scale=2, y=.22, color=color.white, z=-.21)

    def refresh_display():
        display.text = ''.join(keypad_input) if keypad_input else "_"

    def mk_btn(label, pos):
        b = Button(parent=keypad_ui, text=label, scale=(.1,.1), position=pos,
                   color=color.rgb(220,220,220), highlight_color=color.rgb(245,245,245),
                   pressed_color=color.rgb(200,200,200), z=-.21)
        b.text_entity.color = color.black
        return b

    numbers = ['1','2','3','4','5','6','7','8','9']
    start_x, start_y = -0.12, .06
    idx = 0
    for row in range(3):
        for col in range(3):
            n = numbers[idx]; idx += 1
            b = mk_btn(n, (start_x + col*0.12, start_y - row*0.12))
            b.on_click = lambda n=n: (keypad_input.append(n), refresh_display())

    b0   = mk_btn('0', (0, start_y - 3*0.12))
    bdel = mk_btn('Borrar', (-.12, start_y - 3*0.12))
    bok  = mk_btn('OK', (.12, start_y - 3*0.12))

    bdel.on_click = lambda: (keypad_input and keypad_input.pop(), refresh_display())
    def do_ok():
        global keypad_ok
        if keypad_input == keypad_correct:
            keypad_ok = True
            show_prompt("Código correcto (731) ✔", 2)
            destroy_ui()
            try_open_door()
        else:
            show_prompt("Código incorrecto", 2)
            keypad_input.clear(); refresh_display()
    bok.on_click = do_ok

    close_btn = mk_btn('ESC', (.18,.25)); close_btn.scale = (.09,.06)
    close_btn.on_click = destroy_ui

# ==========================
# PORTAL
# ==========================
def create_portal():
    global portal, portal_trigger
    if portal: return
    portal = Entity(model='circle', position=(0, 2, 26.8), scale=3.2,
                    color=color.azure, rotation_x=90, double_sided=True, unlit=True)
    Entity(parent=portal, model='circle', scale=1.15, color=color.rgba(100,200,255,140),
           rotation_x=0, double_sided=True, unlit=True)
    portal_trigger = Entity(position=(0, 1.7, 26.8), scale=(3.0, 3.2, 1.8),
                            collider='box', visible=False)

def animate_portal():
    global _portal_phase
    if portal:
        _portal_phase += time.dt
        portal.rotation_z += time.dt * 50
        portal.scale = 3.2 + 0.06 * math.sin(_portal_phase * 4)

def destroy_portal():
    global portal, portal_trigger
    if portal: destroy(portal); portal = None
    if portal_trigger: destroy(portal_trigger); portal_trigger = None

# ==========================
# PUERTA
# ==========================
def try_open_door():
    global door_opened
    if not door_opened and keypad_ok:
        door_opened = True
        door.animate_y(6, duration=1.2, curve=curve.in_out_sine)
        show_prompt("¡Puerta abierta!", 2.5)
        create_portal()

# ==========================
# ESCENA FINAL 3D (con fallback de modelo)
# ==========================
final_room_entities = []
def create_final_room():
    base = Vec3(100, 0, 0)
    # Grises medios
    floor   = Entity(model='cube', position=base + Vec3(0, -0.05, 0), scale=(12, 0.1, 12),
                     color=color.rgb(120, 120, 120), collider='box', unlit=True)
    wallN   = Entity(model='cube', position=base + Vec3(0, 2.5, -6), scale=(12, 5, 0.2),
                     color=color.rgb(150, 150, 150), collider='box', unlit=True)
    wallS   = Entity(model='cube', position=base + Vec3(0, 2.5,  6), scale=(12, 5, 0.2),
                     color=color.rgb(150, 150, 150), collider='box', unlit=True)
    wallE   = Entity(model='cube', position=base + Vec3( 6, 2.5, 0), scale=(0.2, 5, 12),
                     color=color.rgb(150, 150, 150), collider='box', unlit=True)
    wallW   = Entity(model='cube', position=base + Vec3(-6, 2.5, 0), scale=(0.2, 5, 12),
                     color=color.rgb(150, 150, 150), collider='box', unlit=True)
    ceiling = Entity(model='cube', position=base + Vec3(0, 5.05, 0), scale=(12, 0.1, 12),
                     color=color.rgb(130, 130, 130), collider='box', unlit=True)

    # NPC con fallback: prueba "capsule", si no existe usa "cube"
    try:
        npc = Entity(model='capsule', position=base + Vec3(0, 1, 0), scale=(1, 2, 1),
                     color=color.rgb(120, 160, 255), collider='box', unlit=False)
    except Exception:
        npc = Entity(model='cube', position=base + Vec3(0, 1, 0), scale=(1, 2, 1),
                     color=color.rgb(120, 160, 255), collider='box', unlit=False)

    final_room_entities.extend([floor, wallN, wallS, wallE, wallW, ceiling, npc])

# ==========================
# UI FINAL (LEGIBLE, cubre el 3D)
# ==========================
# ======== UI FINAL (SÚPER LEGIBLE) ========
final_ui = None

def show_final_ui():
    """Overlay negro + texto blanco, forzado al frente."""
    global final_ui
    if final_ui:
        return

    final_ui = Entity(parent=camera.ui)

    # Fondo negro SÓLIDO. z=-0.98 para estar por delante de cualquier overlay anterior.
    bg = Entity(parent=final_ui, model='quad', scale=(2.2, 2.2),
                color=color.rgba(0, 0, 0, 255), z=-0.98)

    # Texto blanco GRANDE centrado, todavía más al frente (z más pequeño = más al frente en la UI)
    Text(parent=final_ui,
         text="...despiertas sobresaltado...\nFue solo un sueño.",
         origin=(0,0),
         scale=2.2,                # grande
         color=color.white,
         z=-0.99)                  # delante del fondo

    # Instrucción chica debajo
    Text(parent=final_ui,
         text="Presiona [Enter] o [ESC] para continuar",
         origin=(0,0),
         scale=1.2,
         color=color.rgba(230,230,230,255),
         position=Vec2(0, -0.14),
         z=-0.99)

    # Bloqueamos control mientras está el overlay
    lock_player(True)

def hide_final_ui():
    global final_ui
    if final_ui:
        destroy(final_ui)
        final_ui = None
    lock_player(False)


# ==========================
# TELEPORT + UI FINAL
# ==========================
def go_to_final_scene():
    destroy_portal()
    create_final_room()
    player.position = Vec3(100, 1.8, -3)
    player.rotation_y = 0
    show_final_ui()

# ==========================
# INPUT
# ==========================
def input(key):
    if key == 'r':
        player.position = Vec3(0, 3, -15)
        show_prompt("Position reset!", 1.5)
        return
    if key == 'escape':
        if final_ui:
            hide_final_ui()
        else:
            destroy_ui()
        return
    if key == 'enter':
        if final_ui:
            hide_final_ui()
            return
    if key == 'e':
        ent = get_interactable()
        if not ent:
            show_prompt("Nada para interactuar.", 1.0); return
        if ent == keypad:
            create_keypad_ui(); return
        if ent == simon:
            show_prompt("Simón fuera de servicio. Usa el Keypad.", 2); return
        if ent == pista_obj:
            show_prompt('PISTA: "731"', 3); return
        if ent == panel_colores:
            show_prompt('COLORES: (no requerido) Usa el Keypad.', 3); return

# ==========================
# UPDATE
# ==========================
def update():
    global end_scene_started
    if player.y < -10:
        player.position = Vec3(0, 3, -15); show_prompt("Respawned!", 2)

    animate_portal()

    if not end_scene_started and door_opened:
        if (portal_trigger and portal_trigger.intersects(player).hit) \
           or (portal and (player.position - portal.position).length() < 2.0 and player.z > 26) \
           or ((player.z > 26.0) and (abs(player.x) < 3.0)):
            end_scene_started = True
            fade_to_black_then(go_to_final_scene, t_in=0.6, t_out=0.6, hold=0.1)
            return

# ==========================
# START
# ==========================
player.position = Vec3(0, 3, -15)
app.run()
