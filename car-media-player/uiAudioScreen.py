from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.properties import (ObjectProperty,
							NumericProperty)
from AudioHandler import AudioHandler
from AudioAlbum import AudioAlbum
from kivy.app import App

AUDIO_SCREEN_KV = '''
#: import ef kivy.uix.effectwidget
<AudioScreen>:
	FloatLayout:
		size: root.size

		# background image
		EffectWidget:
			size: root.size
			effects: ef.VerticalBlurEffect(size=8.0), ef.HorizontalBlurEffect(size=8.0)
			canvas:
				Color:
					rgba: 0.3, 0.3, 0.3, 0.7
				Rectangle:
					pos: self.pos
					size: root.size

			Image:
				size_hint: 1.5, 1.5
				x: root.width * -0.25
				y: root.height * -0.25
			
				texture: root.background_texture
				allow_stretch: True
				keep_ratio: False
		# foreground image
		Image:
			texture: root.background_texture
			allow_stretch: True
			keep_ratio: True
		BoxLayout:
			orientation: 'vertical'
			size_hint: 1, 0.15
			#pos_hint: {"x": 0.2, "y": 0}
			canvas:
				Color:
					rgba: 0.1, 0.1, 0.1, 0.5
				Rectangle:
					size: root.width, self.height
					pos: root.pos
			ProgressBar:
				id: _progress_bar
				pos_hint: {"x": 0.1, "y": 0}
				size_hint: 0.8, 0.33
				max: 1
			BoxLayout:

				pos_hint : {"x": 0.2, "y": 0}
				size_hint: 0.6, 0.66
				spacing: self.width/3


				CircleButton:
					_source: "resources/skip-back.png"
					on_press: root.prev_track()
				CircleButton:
					id: middle_button
					_source: "resources/play.png"
					on_press: root.toggle_play()
				CircleButton:
					_source: "resources/skip-forward.png"
					on_press: root.next_track()
'''

class AudioScreen(Screen):
	background_texture = ObjectProperty()
	progress = NumericProperty()

	def __init__(self, **kwargs) -> None:
		Builder.load_string(AUDIO_SCREEN_KV)
		super().__init__(**kwargs)

	def update(self) -> None:
		"""Update background and play button state"""
		self._update_background()
		self._update_play_button()

	def _update_background(self) -> None:
		"""Updates the picture in the background"""
		self.background_texture = self.manager.audio_handler.get_current_track_image_kv()

	def _update_play_button(self) -> None:
		"""Update the play button's icon"""
		if self.manager.audio_handler.playing:
			self.ids.middle_button._source = 'resources/pause.png'
		else:
			self.ids.middle_button._source = 'resources/play.png'

	def update_slider(self, v):
		"""Updates the slide with the given argument"""
		if 0 <= v <= 1:
			self.ids._progress_bar.value = v


	def toggle_play(self) -> None:
		"""Toggles audio"""
		if self.manager.audio_handler.playing:
			self.manager.audio_handler.pause()
		else:
			self.manager.audio_handler.play_or_resume()
		self.update()

	def change_album_to(self, album:AudioAlbum) -> None:
		self.audio_handler.clear_queue()
		self.audio_handler.load_album_to_queue(album)
		self.audio_handler.change_track_to(0)

	def prev_track(self) -> None:
		self.manager.go_to_previous_track(callback=self.manager.update)

	def next_track(self) -> None:
		self.manager.go_to_next_track(callback=self.manager.update)