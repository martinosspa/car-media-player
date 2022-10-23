
import customtkinter
from typing import Optional

class ImageManipulationFrame(customtkinter.CTkFrame):
	x : int
	y : int
	width : int
	height : int
	blurred : bool = False

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


	def place(self, relx:Optional[float] = 0, 
					rely:Optional[float] = 0, 
					x:Optional[int] = 0,
					y:Optional[int] = 0,
					relwidth:Optional[float] = 0, 
					relheight:Optional[float] = 0,
					width:Optional[int] = 0,
					height:Optional[int] = 0) -> None:

		self.x = int(relx * self.master.width) if not relx == 0 else x
		self.y = int(rely * self.master.height) if not rely == 0 else y
		self.width = int(self.master.width * relwidth) if not relwidth == 0 else width
		self.height = int(self.master.height * relheight) if not relheight == 0 else height
		#print(f'Frame at {self.x},{self.y} {self.width}x{self.height}')
		self.get_background_image()
		if self.blurred:
			from PIL.ImageFilter import GaussianBlur
			self.image.filter(GaussianBlur(3))

		super().place(x=self.x, y=self.y, width=self.width, height=self.height)



	def blur_background_image(self):
		self.blurred = True

	def get_background_image(self):
		from pyscreenshot import grab
		self.image = grab(bbox=(self.x, self.y, 
								self.x + self.width, self.y + self.height))
		#self.image.show()