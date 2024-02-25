from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.properties import ObjectProperty, StringProperty
from kivy.animation import Animation

OPAQUE_IMAGE_BUTTON_KV = '''
<OpaqueImageButton>:
	background_color: 0, 0, 0, 0
	#width: root.width
	#height: root.height
	Image:
		size: root.size
		#color: 1, 1, 1, 1
		pos: root.pos
		source: root._source
'''

SIDEMENU_KV = '''
<SideMenu>:
	BoxLayout:
		width: root.width*2
		height: root.height
		x: root.x
		columns: 2
		canvas:
			Color:
				rgba: 0.1, 0.1, 0.1, 0.5
			Rectangle:
				size: self.size
				pos: self.pos
			
		Button:
			background_color: 0, 0, 0, 0
			size_hint: 0.4, 1
			#text: "debug"
			on_press: root.toggle_screen_size()
		BoxLayout:
			orientation: 'vertical'
			pos: root.pos
			padding: 40, 40, 40, 40
			spacing: 40


			# Button:
			# 	#text: "test1"
			# 	on_press: 
			# 	Image:
			# 		#size: self.size
			# 		#pos: self.pos
			#
			#		source: "resources/music_folder.png"
			#		keep_ratio: True
			OpaqueImageButton:
				_source: "resources/home.png"
				on_press: root.change_screen_to('audio_screen')
			OpaqueImageButton:
				_source: "resources/music_folder.png"
				on_press: root.change_screen_to('album_screen')
			OpaqueImageButton:
				_source: "resources/equalizer.png"
				on_press: root.change_screen_to('equalizer_screen')
'''


class OpaqueImageButton(Button):
	"""Opaque Button that is used for the selecting of other screens"""
	_source = StringProperty()

	def __init__(self, **kwargs) -> None:
		Builder.load_string(OPAQUE_IMAGE_BUTTON_KV)
		super().__init__(**kwargs)

class SideMenu(Widget):
	"""Encapsulates Opaque Image Buttons to select other screens"""
	animation_duration = 0.3 # seconds
	x_opened = 0
	x_closed = 0
	_screen_manager = ObjectProperty()
	opened = False
	
	def __init__(self, **kwargs) -> None:
		Builder.load_string(SIDEMENU_KV)
		super().__init__(**kwargs)

	def toggle_screen_size(self) -> None:
		"""Toggled the side menu screen size"""
		if not self.opened:
			animation = Animation(x=self.x_opened, duration=self.animation_duration, t='in_out_quad')
			animation.start(self)
			self.opened = True

		elif self.opened:
			animation = Animation(x=self.x_closed, duration=self.animation_duration, t='in_out_quad')
			animation.start(self)
			self.opened = False

	def set_opened_to(self, state:bool) -> None:
		"""Sets opened to a certain state"""
		if not (self.opened == state):
			self.toggle_screen_size()

	def change_screen_to(self, screen_name: str) -> None:
		"""Changes the screen to the given screen name"""
		print('change screen received')
		self._screen_manager.current = screen_name
