import customtkinter
from typing import Optional

class AnimatedFrame(customtkinter.CTkFrame):
	width : int
	height : int
	x : int
	y : int
	animation_triggered : bool = False
	_at_final_destination: bool = False
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)



	def set_animation_destination(self, x:int, y:int, animation_duration:Optional[int] = 200) -> None:
		'''Set the destination x,y for the end of the animation and the duration'''
		self._initial_x = self.x
		self._initial_y = self.y
		self._final_x = x
		self._final_y = y
		self._animation_duration = animation_duration

		# these 2 values are floats for bigger animation_duration number thus requiring
		# the actual x, y values to be rounded at the end of the animation
		self._animation_change_x = (self._final_x - self.x)/self._animation_duration
		self._animation_change_y = (self._final_y - self.y)/self._animation_duration

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

		super().place(x=self.x, y=self.y, width=self.width, height=self.height)

	def trigger_animation(self) -> None:
		'''Trigger the animation'''
		if not self.animation_triggered:
			self.place(x=self.x + self._animation_change_x, 
					   y=self.y + self._animation_change_y, 
					   width=self.width, 
					   height=self.height)

			# here round is used to compare the two values
			# because of bigger animation_duration values @ set_animation_destination 
			if round(self.x) == self._final_x and round(self.y) == self._final_y:
				# round the values at the end so there's no future conflicts comparing floats to integers
				self.x = round(self.x)
				self.y = round(self.y)
				self.animation_triggered = True
			self.master.after(1, self.trigger_animation)
				
	def return_to_initial_position(self) -> None:
		'''Return to initial position before set_animation_destination was called''' 
		if self.animation_triggered:
			self.place(x=self.x - self._animation_change_x, 
					   y=self.y - self._animation_change_y, 
					   width=self.width, 
					   height=self.height)

			if round(self.x) == self._initial_x and round(self.y) == self._initial_y:
				# round the values at the end so there's no future conflicts comparing floats to integers
				self.x = round(self.x)
				self.y = round(self.y)
				self.animation_triggered = False
			self.master.after(1, self.return_to_initial_position)


	# This needs to be added because there's a bug in customtkinter
	def bind(self, *args) -> None:
		self.canvas.bind(*args)



