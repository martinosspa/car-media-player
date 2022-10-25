import customtkinter
from AnimatedFrame import AnimatedFrame
from ImageManipulationFrame import ImageManipulationFrame
from AudioHandler import AudioHandler
from screeninfo import get_monitors
from typing import Tuple
from PIL import ImageTk, Image

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


def get_main_monitor_dimensions() -> Tuple[float, float]:
	for monitor in get_monitors():
		if monitor.is_primary:
			return (monitor.width, monitor.height)

class GUI(customtkinter.CTk):
	def __init__(self) -> None:
		super().__init__()
		self.width, self.height = get_main_monitor_dimensions()
		self._main_menu_width = int(self.width * 0.8)
		self._main_menu_height = int(self.height)
		#self.geometry('1024x600')
		self.wm_attributes('-fullscreen', 'True')
		self._setup_main_audio_menu()
		self._setup_side_menu()


	def _setup_main_audio_menu(self) -> None:
		"""This setups the entire audio menu screen and initializes the AudioHandler"""
		self.blurred_frame = None
		self.main_audio_menu = customtkinter.CTkFrame(self)
		# temporary image
		img = Image.open('resources/background.jpeg').resize((self._main_menu_width, self._main_menu_height))
		self.background_image = ImageTk.PhotoImage(img)
		self.main_audio_menu_background = customtkinter.CTkLabel(self.main_audio_menu, image=self.background_image)

		self.main_audio_menu.place(x=0, y=0, width=self._main_menu_width, height=self._main_menu_height)
		self.main_audio_menu_background.place(x=0, y=0)
		self.audio_handler = AudioHandler()
		self.audio_handler.load_queue_from_path()
		self.audio_handler.load_track()



	def _setup_side_menu(self) -> None:
		"""Setup the side menu"""
		self.side_menu = AnimatedFrame(self)
		self.side_menu.place(x=self._main_menu_width,
							 y=0, 
							 width=(self.width - self._main_menu_width), 
							 height=self.height)
		self.side_menu.set_animation_destination(self.width*0.7, 0, animation_duration=3000)
		self.side_menu.bind('<ButtonPress-1>', self.expand_side_menu)

	def retract_side_menu(self) -> None:
		"""Retract the side_menu out and remove the blur"""
		self.side_menu.return_to_initial_position(callback=self.blurred_frame.destroy)
		
	def expand_side_menu(self, event) -> None:
		"""Move the side_menu in to the main widget to reveal the menu buttons 
		while also disabling the main frame and placing a ghost frame 
		to blur and disable the widgets on the main screen"""

		self.blurred_frame = ImageManipulationFrame(self)
		self.blurred_frame.blur_background_image()
		self.blurred_frame.place(x=0, y=0, relwidth=0.7, relheight=1)
		self.side_menu.trigger_animation()
		
		# debug
		self.after(5000, self.retract_side_menu)




if __name__ == "__main__":
	app = GUI()
	app.mainloop()