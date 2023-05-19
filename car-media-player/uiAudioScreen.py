from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, AliasProperty

CIRCLE_BUTTON_KV = '''
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
'''

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
class CircleButton(Button):
	"""Circular buttons, used for skipping and pausing"""
	_source = StringProperty()
	
	def __init__(self, **kwargs) -> None:
		self.scale = AliasProperty(self.get_scale, None, bind=['height'])
		Builder.load_string(CIRCLE_BUTTON_KV)
		super().__init__(**kwargs)

	def get_scale(self) -> NumericProperty:
		return self.height/64



class AudioScreen(Screen):
	"""Screen that encapsulates playing audio and displaying mp3 picture"""
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

	def update_slider(self, new_value):
		"""Updates the slide with the given argument"""
		if 0 <= new_value <= 1:
			self.ids._progress_bar.value = new_value


	def toggle_play(self) -> None:
		"""Toggles audio"""
		if self.manager.audio_handler.playing:
			self.manager.audio_handler.pause()
		else:
			self.manager.audio_handler.play_or_resume()
		self.update()


	def prev_track(self) -> None:
		"""Switches to previous track if any"""
		self.manager.go_to_previous_track(callback=self.manager.update)

	def next_track(self) -> None:
		"""Switches to next track if any"""
		self.manager.go_to_next_track(callback=self.manager.update)
