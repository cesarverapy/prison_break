from ursina import Ursina, Sky, DirectionalLight, AmbientLight, color, camera

def make_app(borderless=False, fov=85):
    app = Ursina(borderless=borderless)
    Sky(color=color.rgb(210, 220, 230))
    DirectionalLight(y=3, z=3, rotation=(45,45,45), shadows=True)
    AmbientLight(color=color.rgba(255,255,255,120))
    camera.fov = fov
    return app
