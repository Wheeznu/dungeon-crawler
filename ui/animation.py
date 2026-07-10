class AnimationEngine:
    def __init__(self):
        self.queue = []
        self.floating_texts = [] 
        self.combat_log = []
        self.shake_frames = 0
        
    def add_event(self, event):
        self.queue.append(event)
        
    def process_tick(self):
        for text in self.floating_texts:
            if text["frames"] % 3 == 0:
                text["y"] -= 1 # float up
            text["frames"] -= 1
            
        self.floating_texts = [t for t in self.floating_texts if t["frames"] > 0]
        
        if self.shake_frames > 0:
            self.shake_frames -= 1
            
        if self.queue and len(self.floating_texts) < 5:
            event = self.queue.pop(0)
            if event["type"] == "DAMAGE":
                crit_str = " (CRITICAL)" if event.get("is_crit") else ""
                self.combat_log.append(f"> {event['source']} serang {event['target']} [-{event['value']} HP]{crit_str}")
                
                self.floating_texts.append({
                    "text": f"-{event['value']}{' CRIT!' if event.get('is_crit') else ''}",
                    "x": 20, 
                    "y": 8,  
                    "color": 1,
                    "frames": 20
                })
                if event.get("is_crit"):
                    self.shake_frames = 5
            elif event["type"] == "HEAL":
                self.combat_log.append(f"> {event['source']} heal {event['target']} [+{event['value']} HP]")
                self.floating_texts.append({
                    "text": f"+{event['value']}",
                    "x": 20, 
                    "y": 8,  
                    "color": 4,
                    "frames": 20
                })
                
            if len(self.combat_log) > 15:
                self.combat_log.pop(0)
