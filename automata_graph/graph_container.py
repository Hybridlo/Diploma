from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import DragBehavior
from kivy.clock import Clock

class GraphContainer(DragBehavior, FloatLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        def delayed_reposition(*args):
            self.x = self.parent.width / 2 - self.width / 2
            self.y = self.parent.height / 2 - self.height / 2

        Clock.schedule_once(delayed_reposition, 2)

    def on_touch_move(self, touch):
        res = super().on_touch_move(touch)

        if self.x <= - self.width + self.parent.width:
            self.x = - self.width + self.parent.width

        if self.y <= - self.height + self.parent.height:
            self.y = - self.height + self.parent.height

        if self.x >= 0:
            self.x = 0

        if self.y >= 0:
            self.y = 0

        return res