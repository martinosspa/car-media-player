import customtkinter
from AnimatedFrame import AnimatedFrame
from ImageManipulationFrame import ImageManipulationFrame
from screeninfo import get_monitors
from typing import Tuple

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


def get_main_monitor_dimensions() -> Tuple[float, float]:
	for monitor in get_monitors():
		if monitor.is_primary:
			return (monitor.width, monitor.height)

class GUI(customtkinter.CTk):
	def __init__(self):
		super().__init__()
		self.width, self.height = get_main_monitor_dimensions()

		#self.geometry('1024x600')
		self.wm_attributes('-fullscreen', 'True')



		self.side_menu = AnimatedFrame(self)
		
		self.side_menu.place(relx=0.8, rely=0, relwidth=0.3, relheight=1)


		print(self.width, self.height)
		print(self.side_menu.width, self.side_menu.height)

		self.side_menu.set_animation_destination(self.width*0.7, 0, animation_duration=300)
		self.side_menu.bind('<ButtonPress-1>', self.expand_side_menu)


	def expand_side_menu(self, event) -> None:
		'''Moves the side_menu in to the main widget to reveal the menu buttons 
		while also disabling the main frame and placing a ghost frame 
		to blur and disable the widgets on the main screen'''
		self.blurred_frame = ImageManipulationFrame(self)
		self.blurred_frame.blur_background_image()
		self.blurred_frame.place(x=0, y=0, relwidth=0.7, relheight=1)
		self.side_menu.trigger_animation()
		
		#self.after(4000, self.side_menu.return_to_initial_position)




if __name__ == "__main__":
	app = GUI()
	app.mainloop()