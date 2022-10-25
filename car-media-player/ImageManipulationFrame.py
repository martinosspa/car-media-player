import customtkinter
from typing import Optional
from PIL.ImageFilter import GaussianBlur
from pyscreenshot import grab
from PIL import Image, ImageTk
class ImageManipulationFrame(customtkinter.CTkFrame):
	"""Custom CTK frame that can manipulate the image it has"""
	x: int
	y: int
	width: int
	height: int
	blurred: bool = False

	def __init__(self, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)
		self.image_label = None
		self.image = None

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
			self.image = self.image.filter(GaussianBlur(radius=3))
		self.image = ImageTk.PhotoImage(self.image)
		self.image_label = customtkinter.CTkLabel(master=self.master, image=self.image)
		# debug
		#self.image.show()
		self.image_label.place(x=self.x, y=self.y, width=self.width, height=self.height)
		
		#super().place(x=self.x, y=self.y, width=self.width, height=self.height)
		
	def destroy(self) -> None:
		"""Removed the frame and it's children"""
		if self.image_label:
			self.image_label.destroy()
		super().destroy()

	def blur_background_image(self) -> None:
		"""Sets the blur flag for when the background image is taken"""
		self.blurred = True

	def get_background_image(self) -> None:
		"""Gets the background image using pyscreenshot"""
		bbox=(self.x, self.y, self.x + self.width, self.y + self.height)
		self.image = grab(bbox)
