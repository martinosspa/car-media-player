from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.slider import Slider

EQUALIZER_SCREEN_KV = '''
<EqualizerScreen>:
	BoxLayout:
		canvas:
			Color:
				rgb: 0.3, 0.3, 0.3, 0.7
			Rectangle:
				size: self.size
		id: layout
		orientation: 'horizontal'
		size_hint_x: 0.9

'''

class EqualizerScreen(Screen):
	def __init__(self, **kwargs) -> None:
		Builder.load_string(EQUALIZER_SCREEN_KV)
		super().__init__(**kwargs)
		for _ in range(10):
			self.ids.layout.add_widget(Slider(min=-10, max=10, step=1, orientation='vertical'))
	
	def update(self) -> None:
		pass
