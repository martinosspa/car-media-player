from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.clock import mainthread
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from AudioHandler import AudioHandler
from uiAudioScreen import AudioScreen
from uiAlbums import AlbumScreen
from uiEqualizer import EqualizerScreen

MAIN_SCREEN_KV = '''
#: import SideMenu uiSidemenu.SideMenu
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

'''

class AudioHandlerScreenManager(ScreenManager):
	"""Screen manager & thread hadling for front-end side"""
	audio_handler: AudioHandler
	_side_menu = ObjectProperty()

	def __init__(self, **kwargs) -> None:
		super().__init__(transition=FadeTransition(), **kwargs)
		
		self.audio_handler = AudioHandler()
		#self.audio_handler.start()

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

	@mainthread # <- NOT removing this, stuff might break
	def update(self) -> None:
		for screen in self.screens:
			screen.update()

	def go_to_previous_track(self, callback=None) -> None:
		self.audio_handler.go_to_previous_track(callback=callback)

	def go_to_next_track(self, callback=None) -> None:
		self.audio_handler.go_to_next_track(callback=callback)
		
class MainScreen(Widget):
	screen_manager = ObjectProperty()

	def __init__(self, **kwargs) -> None:
		Builder.load_string(MAIN_SCREEN_KV)
		super().__init__(**kwargs)

class TestApp(App):
	main_screen = None
	def build(self):
		self.main_screen = MainScreen()
		Window.bind(on_request_close=self.close_audio_handler)
		return self.main_screen

	def change_album_to(self, album) -> None:
		self.main_screen.ids.screen_manager.change_album_to(album)
		self.main_screen.ids.screen_manager.current = 'audio_screen'
		self.main_screen.ids.side_menu.set_opened_to(False)
		self.main_screen.ids.screen_manager.get_screen('audio_screen').update_slider(0)
		
	def close_audio_handler(self, _) -> None:
		self.main_screen.ids.screen_manager.audio_handler.close()




if __name__ == '__main__':
	TestApp().run()
