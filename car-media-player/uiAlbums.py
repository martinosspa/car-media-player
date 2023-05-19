from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.app import App
from AudioAlbum import AudioAlbum

ALBUM_BUTTON_KV = '''
<AlbumButton>:
	background_color: 0, 0, 0, 0
	Image:
		pos: root.pos
		size: root.size
		texture: root.album_texture
		allow_stretch: True
		keep_ratio: True
'''

ALBUM_SCREEN_KV = '''
<AlbumScreen>:
	ScrollView:
		do_scroll_x: False
		do_scroll_y: True
		size_hint_x: 1
		size_hint_y: 1
		GridLayout:
			size_hint_x: 0.9
			size_hint_y: 1.5
			rows: 5
			cols: 5
			id: layout
			col_default_width: self.width/5
			row_default_height: self.height/6
			row_force_default: True
			spacing: 4, 1
'''

class AlbumButton(Button):
	"""Button that contains an ablum picture and transitions to that Album when selected"""
	album:AudioAlbum
	album_texture = ObjectProperty()

	def __init__(self, a:AudioAlbum, **kwargs) -> None:
		Builder.load_string(ALBUM_BUTTON_KV)
		super().__init__(**kwargs)
		self.album = a
		self.album_texture = self.album.get_image_kv()

	def on_press(self) -> None:
		App.get_running_app().change_album_to(self.album)

class AlbumScreen(Screen):
	"""Screen that encapsulates all the Album Buttons"""
	def __init__(self, **kwargs) -> None:
		Builder.load_string(ALBUM_SCREEN_KV)
		super().__init__(**kwargs)
		
	def on_pre_enter(self) -> None:
		self.ids.layout.clear_widgets()
		for album in self.manager.audio_handler.audio_library:
			self.ids.layout.add_widget(AlbumButton(album))

	def update(self) -> None:
		pass
