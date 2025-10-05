from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
from direct.actor.Actor import Actor
import math
from .base_scene import BaseScene


class IntralevelScene(BaseScene):
    """Intralevel: Prison Guard Patrol - Escape the main prison area"""
    
    # Configuration constants
    DEBUG_MODE = False  # Disable debugging
    DEBUG_SHOW_CATCH_ZONE = DEBUG_MODE
    
    # Police Officer Settings
    OFFICER_WALK_SPEED = 2.3
    OFFICER_CATCH_DISTANCE = 5.5
    OFFICER_CATCH_HEIGHT_TOLERANCE = 2.0
    OFFICER_ROTATION_SPEED = 180
    OFFICER_SCALE = 0.01
    OFFICER_HEADING_OFFSET = 90
    
    # Scene Settings
    NUM_TABLES = 3
    TABLE_SPACING = 5
    NUM_CELLS = 5
    CELL_SIZE = 6
    CELL_HEIGHT = 5
    CELL_SPACING = 4.2
    
    # Player Settings
    # Position on upper platform in front of prison cells
    PLAYER_START_POSITION = (-9.1, 7.1, -12.6)  # Adjusted to platform surface
    PLAYER_WALK_SPEED = 5
    PLAYER_RUN_SPEED = 30
    
    def __init__(self, scene_manager=None):
        super().__init__()
        self.scene_manager = scene_manager
        self.player = None
        self.officers = []
        self.game_over = False
        self.game_over_text = None
        self.coordinate_text = None
        self.fade_overlay = None
    
    def setup(self):
        """Initialize the intralevel scene"""
        self.is_active = True
        
        # Create environment
        self._create_sky()
        self._create_player()
        self._create_walls()
        self._create_tables()
        self._create_stairs()
        self._create_floor_planes()
        self._create_doors()
        self._create_prison_cells()
        self._create_ground()
        self._create_ceiling()
        self._create_lighting()
        self._create_officers()
        self._create_ui()
        
        # Final position and control setup
        self.player.position = self.PLAYER_START_POSITION
        self.player.rotation = (0, 0, 0)
        self.player.gravity = 1
        self.player.enabled = True
        
        # Ensure mouse controls work properly
        mouse.locked = True
        self.player.cursor.enabled = True
    
    def _create_sky(self):
        """Create sky"""
        sky = Sky()
        self.entities.append(sky)
    
    def _create_player(self):
        """Create the player character"""
        self.player = FirstPersonController(
            position=self.PLAYER_START_POSITION,
            speed=self.PLAYER_WALK_SPEED,
            origin_y=-.5,
            height=2,
            camera_pivot_y=1
        )
        self.player.gravity = 1
        self.player.cursor.visible = True
        self.player.enabled = True
        self.player.scale = (1, 1, 1)
        
        # Create properly sized collider
        self.player.collider = BoxCollider(self.player, Vec3(0, 1.5, 0), Vec3(2, 3, 2))
        
        self.entities.append(self.player)
    
    def _create_walls(self):
        """Create prison walls"""
        # Left wall (negative z side)
        wall_left = Entity(
            model='cube',
            scale=(40, 10, 0.1),
            position=(2.5, 1.6, -10),
            collider='box',
            shader=lit_with_shadows_shader,
            cast_shadows=True,
            texture='white_cube',
            texture_scale=(5, 2)
        )
        self.entities.append(wall_left)
        
        # Right wall (positive z side)
        wall_right = Entity(
            model='cube',
            scale=(40, 10, 0.1),
            position=(2.5, 1.6, 15),
            collider='box',
            shader=lit_with_shadows_shader,
            cast_shadows=True,
            texture='grass',
            texture_scale=(5, 2)
        )
        self.entities.append(wall_right)
        
        # Front wall (negative x side)
        wall_front = Entity(
            model='cube',
            scale=(0.1, 20, 50),
            position=(-12.5, 1.5, 0),
            collider='box',
            shader=lit_with_shadows_shader,
            cast_shadows=True,
            color=color.green,
            texture_scale=(5, 2)
        )
        self.entities.append(wall_front)
        
        # Back wall (positive x side)
        wall_back = Entity(
            model='cube',
            scale=(0.1, 20, 50),
            position=(5.5, 1.5, 0),
            collider='box',
            shader=lit_with_shadows_shader,
            cast_shadows=True,
            color=color.blue,
            texture_scale=(5, 2)
        )
        self.entities.append(wall_back)
    
    def _create_tables(self):
        """Create prison tables"""
        table_rows = [(5, 'positive z'), (-2, 'negative z')]
        for z_pos, _ in table_rows:
            for i in range(self.NUM_TABLES):
                table = Entity(
                    model='assets/models/prison_table.glb',
                    scale=0.006,
                    position=(i * self.TABLE_SPACING, 0.1, z_pos),
                    rotation=(0, 90, 0),
                    collider='box',
                    shader=lit_with_shadows_shader,
                    cast_shadows=True
                )
                self.entities.append(table)
    
    def _create_stairs(self):
        """Create stairs"""
        stair_1 = Entity(
            model='assets/models/scene.gltf',
            position=(-7, -0.1, -4),
            rotation=(0, 90, 0),
            collider='mesh',  # Changed from mesh to box for better collision
            shader=lit_with_shadows_shader,
            cast_shadows=True,
            scale=2,
            color=color.gray
        )
        self.entities.append(stair_1)
        
        stair_2 = Entity(
            model='assets/models/scene.gltf',
            position=(0, -0.1, 9),
            rotation=(0, -90, 0),
            collider='mesh',  # Changed from mesh to box for better collision
            shader=lit_with_shadows_shader,
            cast_shadows=True,
            scale=2,
            color=color.red
        )
        self.entities.append(stair_2)
    
    def _create_floor_planes(self):
        """Create floor planes"""
        plane_entity = Entity(
            model='plane',
            position=(10, 6.6, -15),
            scale=(60, 1, 10),
            rotation=(0, 0, 0),
            color=color.cyan,
            shader=lit_with_shadows_shader,
            collider='box'
        )
        self.entities.append(plane_entity)
        
        plane_entity_2 = Entity(
            model='plane',
            position=(-18, 6.6, 20),
            scale=(60, 1, 10),
            rotation=(0, 0, 0),
            color=color.cyan,
            shader=lit_with_shadows_shader,
            collider='box'
        )
        self.entities.append(plane_entity_2)
    
    def _create_doors(self):
        """Create doors"""
        # Medical bay entrance
        medical_bay_door = Entity(
            model='assets/models/prison_door.glb',
            position=(2.4, 1, -10),
            scale=(1.5, 2, 3),
            rotation=(0, 0, 0),
            collider='box',
            shader=lit_with_shadows_shader,
            cast_shadows=True
        )
        self.entities.append(medical_bay_door)
        
        # Laundry room entrance
        laundry_room_door = Entity(
            model='assets/models/prison_door.glb',
            position=(-8.4, 1, 14.8),
            scale=(1.5, 2, 3),
            rotation=(0, 0, 0),
            collider='box',
            shader=lit_with_shadows_shader,
            cast_shadows=True
        )
        self.entities.append(laundry_room_door)
    
    def _create_prison_cells(self):
        """Create prison cells"""
        cell_rows_config = [
            (6.6, -17, 0),      # First row
            (6.6, 21.7, -180)   # Second row (flipped)
        ]
        
        for y, z, rotation in cell_rows_config:
            for i in range(self.NUM_CELLS):
                cell_pos = (3 - i * self.CELL_SPACING, y, z)
                cell = self._create_single_prison_cell(cell_pos, rotation_y=rotation)
                self.entities.append(cell)
    
    def _create_single_prison_cell(self, parent_position, rotation_y=0):
        """Create a single prison cell group at the specified position"""
        cell_group = Entity(position=parent_position, rotation=(0, rotation_y, 0))
        
        # Ceiling
        Entity(
            parent=cell_group,
            model='cube',
            position=(0, self.CELL_HEIGHT, 0),
            scale=(self.CELL_SIZE, 0.1, self.CELL_SIZE),
            color=color.dark_gray,
            shader=lit_with_shadows_shader,
            collider='box'
        )
        
        # Front wall
        Entity(
            parent=cell_group,
            model='cube',
            position=(0, self.CELL_HEIGHT/2, self.CELL_SIZE/2),
            scale=(self.CELL_SIZE, self.CELL_HEIGHT, 0.2),
            color=color.gray,
            shader=lit_with_shadows_shader,
            collider='box'
        )
        
        # Prison door
        Entity(
            parent=cell_group,
            model='assets/models/prison_door.glb',
            position=(0, 1, self.CELL_SIZE/2),
            scale=(1.5, 2, 3),
            collider='box',
            shader=lit_with_shadows_shader,
            cast_shadows=True
        )
        
        return cell_group
    
    def _create_ground(self):
        """Create ground"""
        ground = Entity(
            model='plane',
            scale=100,
            position=(0, 0, 0),  # Ensure it's at Y=0
            texture='assets/textures/Ground.png',
            texture_scale=(10, 10),
            collider='box',
            shader=lit_with_shadows_shader,
            visible=True
        )
        self.entities.append(ground)
    
    def _create_ceiling(self):
        """Create ceiling"""
        upper_ceiling = Entity(
            model='cube',
            position=(-3.5, 11, 2.5),
            scale=(25, 0.2, 50),
            color=color.rgb(80, 80, 90),
            shader=lit_with_shadows_shader,
            texture='white_cube',
            texture_scale=(12, 20),
            collider='box',
            cast_shadows=True
        )
        self.entities.append(upper_ceiling)
    
    def _create_lighting(self):
        """Create lighting"""
        ambient = AmbientLight(color=color.rgba(150, 150, 150, 255))
        self.entities.append(ambient)
        
        directional1 = DirectionalLight(
            position=(10, 10, 10),
            rotation=(45, -45, 0),
            shadows=True,
            color=color.white
        )
        self.entities.append(directional1)
        
        directional2 = DirectionalLight(
            position=(-10, 10, -10),
            rotation=(45, 135, 0),
            shadows=False,
            color=color.rgba(200, 200, 220, 255)
        )
        self.entities.append(directional2)
    
    def _create_officers(self):
        """Create police officers"""
        patrol_route = [
            (-10, 0.1, -8),
            (4, 0.1, -8),
            (4, 0.1, 14),
            (-10, 0.1, 14)
        ]
        
        officer = PoliceOfficer(
            start_position=patrol_route[0],
            patrol_waypoints=patrol_route,
            config={
                'walk_speed': self.OFFICER_WALK_SPEED,
                'catch_distance': self.OFFICER_CATCH_DISTANCE,
                'height_tolerance': self.OFFICER_CATCH_HEIGHT_TOLERANCE,
                'rotation_speed': self.OFFICER_ROTATION_SPEED,
                'scale': self.OFFICER_SCALE,
                'heading_offset': self.OFFICER_HEADING_OFFSET,
                'debug_show_catch_zone': self.DEBUG_SHOW_CATCH_ZONE
            }
        )
        self.officers.append(officer)
    
    def _create_ui(self):
        """Create UI elements"""
        self.game_over_text = Text(
            text='',
            origin=(0, 0),
            scale=3,
            color=color.red,
            visible=False
        )
        self.entities.append(self.game_over_text)
        
    def update(self):
        """Update scene logic"""
        if not self.is_active:
            return
        
        # Update officers AI
        for officer in self.officers:
            officer.update_ai(self.player)
            
            # Check for player capture
            if not self.game_over and officer.caught_player:
                self.game_over = True
                self.game_over_text.text = 'CAUGHT!\nPress R to restart'
                self.game_over_text.visible = True
                self.player.speed = 0
                self.player.gravity = 0
    
    def input(self, key):
        """Handle input"""
        if not self.is_active:
            return
        
        # Restart level on 'R' key press
        if key == 'r' and self.game_over:
            self._restart_level()
        
        # Sprint mechanic (Shift key)
        if not self.game_over:
            self.player.speed = self.PLAYER_RUN_SPEED if held_keys['shift'] else self.PLAYER_WALK_SPEED
    
    def _restart_level(self):
        """Restart the current level"""
        self.game_over = False
        self.game_over_text.visible = False
        self.player.position = self.PLAYER_START_POSITION
        self.player.speed = self.PLAYER_WALK_SPEED
        self.player.gravity = 1
        
        # Reset all officers
        for officer in self.officers:
            officer.reset()
    
    def cleanup(self):
        """Clean up scene resources"""
        # Clean up officers
        for officer in self.officers:
            officer.destroy()
        self.officers.clear()
        
        # Clean up entities
        super().cleanup()


# =============================================================================
# POLICE OFFICER CLASS
# =============================================================================
class PoliceOfficer:
    """AI-controlled police officer with patrol and catch behavior"""
    
    def __init__(self, start_position, patrol_waypoints, config):
        self.state = 'patrol'
        self.patrol_waypoints = patrol_waypoints
        self.current_waypoint = 0
        self.caught_player = False
        self.start_position = start_position
        
        # Configuration
        self.walk_speed = config['walk_speed']
        self.catch_distance = config['catch_distance']
        self.height_tolerance = config['height_tolerance']
        self.rotation_speed = config['rotation_speed']
        self.scale = config['scale']
        self.heading_offset = config['heading_offset']
        
        # Create actor with holder entity
        self.actor = Actor('assets/models/police_officer_walking.glb')
        self.actor.loadAnims({'Walk': 'assets/models/police_officer_walking.glb'})
        
        self.holder = Entity(position=start_position, scale=self.scale)
        self.actor.reparentTo(self.holder)
        self.actor.setTwoSided(True)
        self.actor.setH(self.heading_offset)
        self.actor.loop('Walk')
        
        # Catch zone indicator
        self.catch_zone_indicator = Entity(
            model='circle',
            position=(start_position[0], start_position[1] + 0.05, start_position[2]),
            scale=(self.catch_distance * 2, self.catch_distance * 2, 1),
            rotation_x=90,
            color=color.rgba(255, 0, 0, 10),
            unlit=True,
            visible=config['debug_show_catch_zone']
        )
    
    def get_distance_to_player(self, player):
        """Calculate horizontal distance to player (ignoring Y axis)"""
        dx = player.x - self.holder.x
        dz = player.z - self.holder.z
        return math.sqrt(dx * dx + dz * dz)
    
    def is_player_on_same_level(self, player):
        """Check if player is on the same vertical level"""
        return abs(player.y - self.holder.y) < self.height_tolerance
    
    def move_towards(self, target_pos, speed):
        """Move officer towards a target position"""
        dx = target_pos[0] - self.holder.x
        dz = target_pos[2] - self.holder.z
        distance = math.sqrt(dx * dx + dz * dz)
        
        if distance > 0.1:
            # Normalize and move
            direction_x = dx / distance
            direction_z = dz / distance
            self.holder.x += direction_x * speed * time.dt
            self.holder.z += direction_z * speed * time.dt
            
            # Update catch zone indicator
            self.catch_zone_indicator.x = self.holder.x
            self.catch_zone_indicator.z = self.holder.z
            
            # Update rotation
            angle = math.degrees(math.atan2(direction_x, direction_z)) - self.heading_offset
            self.holder.rotation_y = angle
    
    def patrol_behavior(self, player):
        """Handle patrol along waypoints"""
        if not self.patrol_waypoints:
            return
        
        # Check for player capture
        if self.is_player_on_same_level(player):
            if self.get_distance_to_player(player) <= self.catch_distance:
                self.state = 'caught'
                self.caught_player = True
                self.actor.stop()
                return
        
        # Patrol movement
        target = self.patrol_waypoints[self.current_waypoint]
        dx = target[0] - self.holder.x
        dz = target[2] - self.holder.z
        distance_to_waypoint = math.sqrt(dx * dx + dz * dz)
        
        if distance_to_waypoint < 0.5:
            self.current_waypoint = (self.current_waypoint + 1) % len(self.patrol_waypoints)
        else:
            self.move_towards(target, self.walk_speed)
    
    def update_ai(self, player):
        """Main AI update loop"""
        if self.state == 'caught':
            self._rotate_to_face_player(player)
        elif self.state == 'patrol':
            self.patrol_behavior(player)
    
    def _rotate_to_face_player(self, player):
        """Smoothly rotate officer to face the player"""
        dx = player.x - self.holder.x
        dz = player.z - self.holder.z
        
        if abs(dx) < 0.01 and abs(dz) < 0.01:
            return
        
        target_angle = math.degrees(math.atan2(dx, dz)) - self.heading_offset
        current = self.holder.rotation_y
        diff = target_angle - current
        
        # Normalize to [-180, 180]
        while diff > 180:
            diff -= 360
        while diff < -180:
            diff += 360
        
        # Apply smooth rotation
        if abs(diff) > 0.5:
            rotation_step = self.rotation_speed * time.dt
            if abs(diff) < rotation_step:
                self.holder.rotation_y = target_angle
            else:
                self.holder.rotation_y += rotation_step if diff > 0 else -rotation_step
    
    def reset(self):
        """Reset officer to initial state"""
        self.state = 'patrol'
        self.current_waypoint = 0
        self.caught_player = False
        self.actor.loop('Walk')
        self.holder.position = self.start_position
        self.catch_zone_indicator.position = (self.start_position[0], self.start_position[1] + 0.05, self.start_position[2])
    
    def destroy(self):
        """Clean up officer resources"""
        if hasattr(self, 'actor') and self.actor:
            self.actor.cleanup()
        if hasattr(self, 'holder') and self.holder:
            self.holder.destroy()
        if hasattr(self, 'catch_zone_indicator') and self.catch_zone_indicator:
            self.catch_zone_indicator.destroy()