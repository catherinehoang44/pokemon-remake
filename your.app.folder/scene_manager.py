"""
Scene Manager
Handles scene transitions and state management
"""


class SceneManager:
    def __init__(self):
        self.scenes = {}
        self.current_scene = None
        self.current_scene_name = None
    
    def register_scene(self, name, scene):
        """Register a scene with a name"""
        self.scenes[name] = scene
    
    def change_scene(self, name):
        """Change to a different scene"""
        if name in self.scenes:
            # Call on_exit on current scene if it exists
            if self.current_scene:
                if hasattr(self.current_scene, 'on_exit'):
                    self.current_scene.on_exit()
            
            # Switch to new scene
            self.current_scene_name = name
            self.current_scene = self.scenes[name]
            
            # Call on_enter on new scene
            if hasattr(self.current_scene, 'on_enter'):
                self.current_scene.on_enter()
        else:
            print(f"Warning: Scene '{name}' not found")
    
    def handle_event(self, event):
        """Pass event to current scene"""
        if self.current_scene:
            self.current_scene.handle_event(event)
    
    def update(self):
        """Update current scene"""
        if self.current_scene:
            self.current_scene.update()
    
    def render(self, screen):
        """Render current scene"""
        if self.current_scene:
            self.current_scene.render(screen)















