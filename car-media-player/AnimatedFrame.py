import customtkinter
from typing import Optional

class AnimatedFrame(customtkinter.CTkFrame):
	width : int
	height : int
	x : int
	y : int
	expanded : bool = False
	_at_final_destination: bool = False
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)



	def set_animation_destination(self, x:int, y:int, time:Optional[int] = 200) -> None:
		self._final_x = x
		self._final_y = y
		print(self._final_x, self._final_y)
		self._animation_duration = time
		self._animation_change_x = round((self._final_x - self.x)/self._animation_duration)
		self._animation_change_y = round((self._final_y - self.y)/self._animation_duration)

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
		print(f'Frame at {self.x},{self.y} {self.width}x{self.height}')

		super().place(x=self.x, y=self.y, width=self.width, height=self.height)

	def move_frame(self) -> None:
		if not self.expanded:

			self.place(x=self.x + self._animation_change_x, 
					   y=self.y + self._animation_change_y, 
					   width=self.width, 
					   height=self.height)

			if self.x == self._final_x and self.y == self._final_y:
				self.expanded = True
			self.master.after(1, self.move_frame)
				

	# This needs to be added because there's a bug in customtkinter
	def bind(self, *args) -> None:
		self.canvas.bind(*args)



