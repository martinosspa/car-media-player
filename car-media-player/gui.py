
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
from kivy.uix.screenmanager import Screen, ScreenManager

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
			text: "debug"
			on_press: root.toggle_screen_size()
		BoxLayout:
			orientation: 'vertical'
			pos: root.pos
			padding: 40, 0, 40, 0
			Button:
				text: "test1"
				on_press: root.change_screen_to('album_screen')
			Button:
				text: "test2"
				on_press: root.change_screen_to('audio_screen')
				
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

		
<MainScreen>:
	id: main_screen
	FloatLayout:
		size: root.size
		AudioHandlerScreenManager
			id: screen_manager
			# Screens are set in code
				
		SideMenu:
			size_hint: 0.1, 1
			x: root.width * 0.9
			x_closed: root.width * 0.9
			x_opened: root.width * 0.8
			_screen_manager: screen_manager

''')

class CircleButton(Button):
	
	def get_scale(self) -> NumericProperty:
		return self.height/64

	_source = StringProperty()
	scale = AliasProperty(get_scale, None, bind=['height'])
	def __init__(self, **kwargs) -> None:
		super(CircleButton, self).__init__(**kwargs)


class AlbumButton(Button):
	pass
class AlbumScreen(Screen):
	
	def on_pre_enter(self) -> None:
		for i in range(6):
			self.ids.layout.add_widget(AlbumButton(text=str(i)))

	def update(self) -> None:
		pass

class AudioScreen(Screen):
	audio_handler : AudioHandler
	background_texture = ObjectProperty()
	progress = NumericProperty()


	def __init__(self, **kwargs) -> None:
		super(AudioScreen, self).__init__(**kwargs)

	def update(self) -> None:
		"""Update background and play button state"""
		self._update_background()
		self._update_play_button()

	def _update_background(self) -> None:
		"""Updates the picture in the background"""
		pil_image, extension = self.manager.audio_handler.get_current_track_image()
		# Convert pil image to kivy image
		data = BytesIO()
		pil_image.save(data, format=extension)
		data.seek(0)
		im = coreImage(BytesIO(data.read()), ext=extension)
		self.background_texture = im.texture

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

	def prev_track(self) -> None:
		self.manager.go_to_previous_track(callback=self.manager.update)
	def next_track(self) -> None:
		self.manager.go_to_next_track(callback=self.manager.update)

class SideMenu(Widget):
	animation_duration = 0.3 # seconds
	x_opened = 0
	x_closed = 0
	_screen_manager = ObjectProperty()
	def __init__(self, **kwargs) -> None:
		super(SideMenu, self).__init__(**kwargs)
		self.opened = False
		
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

	def change_screen_to(self, screen_name: str) -> None:
		self._screen_manager.current = screen_name

class AudioHandlerScreenManager(ScreenManager):
	audio_handler: AudioHandler

	def __init__(self, **kwargs) -> None:
		super(AudioHandlerScreenManager, self).__init__(**kwargs)

		self.add_widget(AudioScreen(name='audio_screen'))
		self.add_widget(AlbumScreen(name='album_screen'))

		self.audio_handler = AudioHandler()
		self.audio_handler.start()

		# temporary
		self.audio_handler.load_album_to_queue(self.audio_handler.audio_library.get(0))
		for track in self.audio_handler.audio_library.get(0):
			print(track)

		self.audio_handler.set_progress_callback(self.get_screen('audio_screen').update_slider)
		self.audio_handler.set_change_callback(self.update)
		self.audio_handler.load_track()

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
		Window.bind(on_request_close=lambda _: self.MS.ids.screen_manager.audio_handler.close())
		return self.MS


if __name__ == '__main__':
	TestApp().run()
