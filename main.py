from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# set sky as background
Sky(texture='sky_default')

# set ground
ground = Entity(model='plane', scale=(100,1,100), texture='Prision_Cell/Ground.png', texture_scale=(10,10), collider='box')
    

# initialize camera at origin(player)
camera.position = (0, 0, 0)
camera.rotation = (0, 0, 0)

# set first person
player = FirstPersonController()

app.run()