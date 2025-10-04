from ursina import Text, color, camera, Entity, invoke

def _clamp(v, a, b):
    return max(a, min(b, v))

class HUD:
    def __init__(self):
        # === Panel del prompt (abajo-centro), inicia oculto ===
        # Usamos origin (0,0) para centrar el rectángulo en su posición.
        self.prompt_bg = Entity(
            parent=camera.ui, model='quad',
            color=color.rgba(0, 0, 0, 190),
            origin=(0, 0),
            position=(0, -0.42),     # centrado horizontal, un poco arriba del borde inferior
            scale=(0.001, 0.001),
            enabled=False,
            z=0,
        )

        # === Texto (hermano del panel) alineado con la misma posición ===
        self.prompt_text = Text(
            parent=camera.ui,
            text='',
            origin=(0, 0),
            position=(0, -0.42),     # misma posición que el panel
            scale=1.2,
            color=color.rgb(255, 255, 0),
            background=False,
        )
        self.prompt_text.z = -0.02   # delante del panel

        # === Estado/progreso (arriba-derecha) ===
        self.state_bg = Entity(
            parent=camera.ui, model='quad',
            color=color.rgba(40, 40, 40, 150),
            origin=(.5, .5), position=(.95, .48),
            scale=(0.28, 0.10), z=0
        )
        self.state_text = Text(
            parent=camera.ui, text='',
            origin=(.5, .5),
            position=(.95, .48),
            scale=0.9, color=color.lime, background=False
        )
        self.state_text.z = -0.02

    # ===== Internos =====
    def _resize_prompt_bg(self, pad_x=0.06, pad_y=0.05, max_w=0.9):
        """Ajusta el tamaño del panel según el tamaño real del Texto."""
        w = self.prompt_text.width
        h = self.prompt_text.height
        if not w or not h:
            # Estimación simple si aún no calculó ancho/alto reales
            lines = (self.prompt_text.text or '').split('\n')
            avg_len = max((len(s) for s in lines), default=0)
            w = 0.018 * avg_len
            h = 0.045 * max(len(lines), 1)

        w = _clamp(w + pad_x, 0.18, max_w)
        h = _clamp(h + pad_y, 0.06, 0.28)
        self.prompt_bg.scale = (w, h)

        # re-centrar por si la posición cambió
        self.prompt_bg.position = (0, -0.42)
        self.prompt_text.position = (0, -0.42)

    def _show_prompt(self, txt: str):
        self.prompt_text.text = txt or ''
        if self.prompt_text.text.strip():
            self.prompt_bg.enabled = True
            self._resize_prompt_bg()
            invoke(self._resize_prompt_bg, delay=0)   # recalcular en el próximo frame
        else:
            self.prompt_bg.enabled = False

    # ===== API pública =====
    def set_prompt(self, txt: str):
        self._show_prompt(txt)

    def set_actions(self, actions):
        """Lista de acciones (list[str]) o str con saltos de línea."""
        if isinstance(actions, (list, tuple)):
            txt = '\n'.join(actions)
        else:
            txt = str(actions or '')
        self._show_prompt(txt)

    def set_progress(self, d: int, t: int):
        self.state_text.text = f'Progreso: {d}/{t}'

    def render_objectives(self, tm):
        pass
