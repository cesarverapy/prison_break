
# Cambios aplicados (fix Sink no interactuable)

- game.py:
  - Importado `held_keys` desde `ursina`.
  - Añadido/reescrito `Game.update()` para seleccionar el interactuable más cercano según el estado de las tareas y aceptar `E` de forma robusta (evita early-returns que bloqueen otros objetos).
- src/world/interactables.py:
  - `Interactable.can_interact` ahora ignora entidades deshabilitadas y sigue midiendo distancia 2D.
  - `Sink` ahora asegura `collider='box'` y extiende `interact_distance` a 3.2 para que siga siendo accesible tras moverlo o pegarlo a una pared.

> Nota: Si usas mapas ASCII, el método `place()` en `Game` conserva la altura `y` original del objeto. Si tu `Sink` queda con `y=0` hundido o muy alto, ajusta `position=(x, 0.45, z)` o similar tras el `place()`.
