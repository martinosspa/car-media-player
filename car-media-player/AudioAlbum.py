from PIL.Image import Image
from typing import Optional, Union
from AudioFile import AudioFile

class AudioAlbum:
	"""Class that contains songs of the same album. Is iterable"""

	def __init__(self, name:str, artist:str, image:Optional[Union[Image, None]]=None) -> None:
		self.name = name
		self.artist = artist
		self.image = image
		self.size = 0
		self._audio_files = []

	def get_image(self) -> Image:
		"""Get the image of the album as a PIL Image"""
		return self.image

	def add_audio_file(self, path) -> None:
		"""Adds an audio file given the path of the file"""
		self._audio_files.append(AudioFile(path, album=self))
		self.size = len(self._audio_files)

	def __iter__(self):
		self._index = 0
		return self

	def __next__(self):
		if self._index < len(self._audio_files):
			r = self._audio_files[self._index]
			self._index += 1
			return r
		else:
			raise StopIteration

	def __repr__(self) -> str:
		return f'{self.artist} - {self.name}'
	
	def __eq__(self, other) -> bool:
		return other.name == self.name and other.artist == self.artist


