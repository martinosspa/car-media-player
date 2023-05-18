from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.properties import (ObjectProperty, 
							StringProperty, 
							NumericProperty, 
							BoundedNumericProperty, 
							BooleanProperty,
							AliasProperty)
from kivy.uix.slider import Slider
from kivy.clock import mainthread
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition

from AudioHandler import AudioHandler
from AudioAlbum import AudioAlbum

from uiAudioScreen import AudioScreen, CircleButton
from uiAlbums import AlbumScreen, AlbumButton
from uiSidemenu import SideMenu, OpaqueImageButton

kv_file = Builder.load_string('''
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
