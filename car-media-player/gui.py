from kivy.app import App
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.anchorlayout import AnchorLayout
from kivy.lang import Builder
from kivy.properties import (ObjectProperty, 
							StringProperty, 
							NumericProperty, 
							BoundedNumericProperty, 
							BooleanProperty,
							AliasProperty)
from kivy.uix.image import Image as uixImage
from kivy.uix.slider import Slider

from AudioHandler import AudioHandler
from AudioAlbum import AudioAlbum
from kivy.animation import Animation

from kivy.clock import mainthread
from kivy.graphics.texture import Texture
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition

from uiAudioScreen import AudioScreen
from uiAlbums import AlbumScreen, AlbumButton


kv_file = Builder.load_string('''
<OpaqueImageButton>:
	background_color: 0, 0, 0, 0
	#width: root.width
	#height: root.height
	Image:
		size: root.size
		#color: 1, 1, 1, 1
		pos: root.pos
		source: root._source
		allow_stretch: True
		keep_ratio: True

<CircleButton>:
	background_color: 0, 0, 0, 0
	width: root.height
	canvas:
		PushMatrix:
		Color:
			rgba: [0.3, 0.3, 0.3, 0.5] if root.state == "normal" else [1, 0.3, 0.3, 0.5]
		Translate:
			x: root.x + root.width/2 - self.height/2
			y: root.y
		Ellipse:
			size: [root.height, root.height]
			pos: 0, 0
		PopMatrix:
	Image:
		size: root.size
		x: root.x 
		y: root.y 
		source: root._source
		color: [0.5, 0.5, 0.5, 0.5] if root.state == "normal" else [1, 0.3, 0.3, 0.5]
		allow_stretch: True
		keep_ratio: True

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

		
<MainScreen>:
	id: main_screen
	FloatLayout:
		size: root.size
		AudioHandlerScreenManager
			id: screen_manager
			# Screens are set in code
				
		SideMenu:
			id: side_menu
			size_hint: 0.1, 1
			x: root.width * 0.9
			x_closed: root.width * 0.9
			x_opened: root.width * 0.8
			_screen_manager: screen_manager

''')
class OpaqueImageButton(Button):
	_source = StringProperty()

class CircleButton(Button):
	def get_scale(self) -> NumericProperty:
		return self.height/64

	_source = StringProperty()
	scale = AliasProperty(get_scale, None, bind=['height'])

	
class SideMenu(Widget):
	animation_duration = 0.3 # seconds
	x_opened = 0
	x_closed = 0
	_screen_manager = ObjectProperty()
	opened = False
		
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
		print('change screen received')
		self._screen_manager.current = screen_name

class EqualizerScreen(Screen):
	def __init__(self, **kwargs) -> None:
		super().__init__(**kwargs)
		for _ in range(10):
			self.ids.layout.add_widget(Slider(min=-10, max=10, step=1, orientation='vertical'))
	
	def update(self) -> None:
		pass






class AudioHandlerScreenManager(ScreenManager):
	audio_handler: AudioHandler
	_side_menu = ObjectProperty()

	def __init__(self, **kwargs) -> None:
		super().__init__(transition=FadeTransition(), **kwargs)
		
		self.audio_handler = AudioHandler()
		self.audio_handler.start()

		self.add_widget(AudioScreen(name='audio_screen'))
		self.add_widget(AlbumScreen(name='album_screen'))
		self.add_widget(EqualizerScreen(name='equalizer_screen'))

		# temporary
		self.audio_handler.load_album_to_queue(self.audio_handler.audio_library.get(0))

		self.audio_handler.set_progress_callback(self.get_screen('audio_screen').update_slider)
		self.audio_handler.set_change_callback(self.update)
		
		

		self.update()
	

	def change_album_to(self, album_name: str) -> None:
		self.audio_handler.clear_queue()
		self.audio_handler.load_album_to_queue(album_name)
		self.update()
		


	@mainthread
	def update(self) -> None:
		for screen in self.screens:
			screen.update()

	def go_to_previous_track(self, callback=None) -> None:
		self.audio_handler.go_to_previous_track(callback=callback)

	def go_to_next_track(self, callback=None) -> None:
		self.audio_handler.go_to_next_track(callback=callback)
		
class MainScreen(Widget):
	screen_manager = ObjectProperty()

class TestApp(App):
	def build(self):
		self.MS = MainScreen()
		Window.bind(on_request_close=self.close_audio_handler)
		return self.MS

	def change_album_to(self, album) -> None:
		self.MS.ids.screen_manager.change_album_to(album)
		self.MS.ids.screen_manager.current = 'audio_screen'
		self.MS.ids.side_menu.set_opened_to(False)
		self.MS.ids.screen_manager.get_screen('audio_screen').ids._progress_bar.value = 0

	def close_audio_handler(self, _) -> None:
		self.MS.ids.screen_manager.audio_handler.close()




if __name__ == '__main__':
	TestApp().run()
