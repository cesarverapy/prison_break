from abc import ABC, abstractmethod
from ursina import destroy


class BaseScene(ABC):
    """Abstract base class for all game scenes"""
    
    def __init__(self):
        self.entities = []
        self.systems = {}
        self.is_active = False
    
    @abstractmethod
    def setup(self):
        """Initialize the scene - must be implemented by subclasses"""
        pass
    
    def update(self):
        """Update scene logic - can be overridden by subclasses"""
        pass
    
    def input(self, key):
        """Handle input - can be overridden by subclasses"""
        pass
    
    def cleanup(self):
        """Clean up scene resources"""
        # Set inactive FIRST to stop any ongoing updates
        self.is_active = False
        
        # Destroy all entities created by this scene using global destroy() function
        for entity in self.entities:
            try:
                destroy(entity)
            except:
                pass
        
        self.entities.clear()
        self.systems.clear()
