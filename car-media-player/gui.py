
from kivy.core.window import Window
from kivy.uix.scatter import Scatter
from kivy.graphics.svg import Svg
from kivy.app import App
from kivy.uix.image import Image
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
from kivy.core.image import Image as coreImage
from AudioHandler import AudioHandler
from kivy.animation import Animation
from io import BytesIO
from kivy.clock import mainthread
from kivy.graphics.texture import Texture
kv_file = Builder.load_string('''
#: import ef kivy.uix.effectwidget
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
	Button:
		size: root.size
		pos: root.pos
		background_color: 0, 0, 0, 0
		canvas:
			Color:
				rgba: 0.3, 0.3, 0.3, 0.5
			
			Rectangle:
				size: root.width, root.height
				pos: root.pos
		text: "debug"
		on_press: root.toggle_screen_size()

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
			Slider:
				id: _progress_slider
				pos_hint: {"x": 0.1, "y": 0}
				size_hint: 0.8, 0.33
				value_track_width: 4
				value_track: True
				value_track_color: [1, 0, 0, 1]
				value_normalized: root.get_progress()
			
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

			


		
<MainScreen>:
	FloatLayout:
		size: root.size
		AudioScreen:
			id: audio_screen
			pos_hint: {"top": 1}
			size_hint: 0.9, 1
		SideMenu:
			pos_hint: {"right": 1}
			size_hint_y: 1
			size_hint_x: 0.1
''')

class CircleButton(Button):
	
	def get_scale(self) -> NumericProperty:
		return self.height/64

	_source = StringProperty()
	scale = AliasProperty(get_scale, None, bind=['height'])
	def __init__(self, **kwargs) -> None:
		super(CircleButton, self).__init__(**kwargs)

	def debug(self):
		print(self.scale)


class AudioScreen(Widget):
	audio_handler : AudioHandler
	background_texture = ObjectProperty()
	def get_progress(self) -> float:
		return self.audio_handler._current_progress

	audio_progress = AliasProperty(get_progress, None)

	def __init__(self, **kwargs) -> None:

		super(AudioScreen, self).__init__(**kwargs)
		self.audio_handler = AudioHandler()
		self.audio_handler.load_queue_from_path('audio/')
		self.audio_handler.set_progress_callback(self.update_slider)
		self.audio_handler.set_change_callback(self.update_background)
		self.audio_handler.load_track()
		self.audio_handler.start()
		
		self.update_background()

	def update_background(self) -> None:
		pil_image, extension = self.audio_handler.get_current_track_image()
		if not pil_image:
			t = Texture.create(size=(64, 64), colorfmt='RGBA', bufferfmt='ubyte')
			s = b'\x00\x00\x00\x80' * 64 * 64
			print(type(s))
			t.blit_buffer(s, colorfmt='rgba')
			self.background_texture = t
			return
		data = BytesIO()
		pil_image.save(data, format=extension)
		data.seek(0)
		im = coreImage(BytesIO(data.read()), ext=extension)
		self.background_texture = im.texture

	def update_slider(self, v):
		if 0 <= v <= 1:
			self.ids._progress_slider.value_normalized = v


	def update_play_button(self) -> None:
		if self.audio_handler.playing:
			self.ids.middle_button._source = 'resources/pause.png'
		else:
			self.ids.middle_button._source = 'resources/play.png'

	def toggle_play(self) -> None:
		if self.audio_handler.playing:
			self.audio_handler.pause()
		else:
			self.audio_handler.play_or_resume()
		self.update_play_button()
			

	def prev_track(self) -> None:
		self.audio_handler.go_to_previous_track(callback=self.update_background)
		self.update_play_button()

	def next_track(self) -> None:
		self.audio_handler.go_to_next_track(callback=self.update_background)
		self.update_play_button()

	def debug(self, t) -> None:
		print(self.x, self.y, self.width, self.height)

class SideMenu(Widget):
	closed_width = 0.1
	opened_width = 0.3
	animation_duration = 0.3 # seconds
	def __init__(self, **kwargs) -> None:
		super(SideMenu, self).__init__(**kwargs)
		self.size_hint_x = self.closed_width
		
	def toggle_screen_size(self) -> None:
		"""Toggled the side menu screen size"""
		if self.size_hint_x == self.closed_width:
			animation = Animation(size_hint_x=self.opened_width, duration=self.animation_duration, t='in_out_quad')
			animation.start(self)

		elif self.size_hint_x == self.opened_width:
			animation = Animation(size_hint_x=self.closed_width, duration=self.animation_duration, t='in_out_quad')
			animation.start(self)
		
class MainScreen(Widget):
	pass

class TestApp(App):
	def build(self):
		MS = MainScreen()
		Window.bind(on_request_close=lambda _: MS.ids.audio_screen.audio_handler.close())
		return MS


if __name__ == '__main__':
	TestApp().run()
