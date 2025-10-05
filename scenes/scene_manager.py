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
    
    def load_scene(self, scene_name, **kwargs):
        """Load a scene by name with optional parameters"""
        if scene_name not in self.scenes:
            return
        
        # Cleanup current scene
        if self.current_scene:
            # Destroy all entities
            for entity in self.current_scene.entities:
                try:
                    if entity and hasattr(entity, 'destroy'):
                        entity.destroy()
                    elif entity and hasattr(entity, 'disable'):
                        entity.disable()
                except Exception:
                    pass
            
            self.current_scene.cleanup()
            self.current_scene = None
        
        # Create and initialize new scene with optional parameters
        scene_class = self.scenes[scene_name]
        try:
            self.current_scene = scene_class(scene_manager=self, **kwargs)
        except TypeError:
            self.current_scene = scene_class()
        self.current_scene.setup()
    
    def update(self):
        """Update current scene"""
        if self.current_scene:
            self.current_scene.update()
    
    def input(self, key):
        """Handle input for current scene"""
        if self.current_scene:
            self.current_scene.input(key)
