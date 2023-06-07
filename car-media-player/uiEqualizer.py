from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.slider import Slider
from kivy.app import App

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
	"""Screen that encapsulates the equalizer setup"""
	
	def __init__(self, **kwargs) -> None:
		Builder.load_string(EQUALIZER_SCREEN_KV)
		super().__init__(**kwargs)
		self.sliders = [Slider(min=-10, max=10, step=1, orientation='vertical') for _ in range(10)]
		for slider in self.sliders:
			self.ids.layout.add_widget(slider)
	
	def update(self) -> None:
		# standard for all screens
		pass

	def on_touch_move(self, touch):
		slider_values = [int(slider.value) for slider in self.sliders]
		App.get_running_app().set_equalizer_values(slider_values)
		return super().on_touch_move(touch)

