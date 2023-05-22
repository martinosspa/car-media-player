from typing import Optional, Union
from io import BytesIO
from kivy.core.image import Image as kvImage
from PIL.Image import Image
from AudioFile import AudioFile

class AudioAlbum:
	"""Class that contains songs of the same album. Is iterable"""
	_index = 0
	def __init__(self, name:str, artist:str, image:Optional[Union[Image, None]]=None, image_extension=None) -> None:
		self.name = name
		self.artist = artist
		self.image = image
		self.image_extension = image_extension
		self.size = 0
		self._audio_files = []
		# Load the image as a kv object as well to not load 
		# it every time during run time
		if self.image and self.image_extension:
			data = BytesIO()
			self.image.save(data, format=self.image_extension)
			data.seek(0)
			image = kvImage(BytesIO(data.read()), ext=self.image_extension)
			self.kv_image = image.texture

	def get_image(self) -> [Image, str]:
		"""Get the image of the album as a PIL Image"""
		return [self.image, self.image_extension]

	def get_image_kv(self) -> kvImage:
		"""Returns the KV image"""
		return self.kv_image

	def add_audio_file(self, path) -> None:
		"""Adds an audio file given the path of the file"""
		self._audio_files.append(AudioFile(path, album=self))
		self.size = len(self._audio_files)

	def __iter__(self):
		self._index = 0
		return self

	def __next__(self):
		if self._index < len(self._audio_files):
			_next = self._audio_files[self._index]
			self._index += 1
			return _next
		raise StopIteration

	def __repr__(self) -> str:
		return f'{self.artist} - {self.name}'
	
	def __eq__(self, other) -> bool:
		return other.name == self.name and other.artist == self.artist

	def close(self) -> None:
		"""Safely close"""
		for file in self._audio_files:
			file.close()

