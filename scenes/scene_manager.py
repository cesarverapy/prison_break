from ursina import *


class SceneManager:
    """Manages scene transitions and current scene state"""
    
    def __init__(self):
        self.current_scene = None
        self.scenes = {}
        self.app = None
    
    def setup(self, app):
        """Initialize with Ursina app instance"""
        self.app = app
    
    def register_scene(self, name, scene_class):
        """Register a scene class with a name"""
        self.scenes[name] = scene_class
    
    def load_scene(self, scene_name):
        """Load a scene by name"""
        if scene_name not in self.scenes:
            print(f"Scene '{scene_name}' not found!")
            return
        
        # Clean up current scene
        if self.current_scene:
            self.current_scene.cleanup()
        
        # Create and initialize new scene
        scene_class = self.scenes[scene_name]
        self.current_scene = scene_class()
        self.current_scene.setup()
        
        print(f"Loaded scene: {scene_name}")
    
    def update(self):
        """Update current scene"""
        if self.current_scene:
            self.current_scene.update()
    
    def input(self, key):
        """Handle input for current scene"""
        if self.current_scene:
            self.current_scene.input(key)
