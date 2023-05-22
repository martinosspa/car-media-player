from io import BytesIO
from typing import Tuple
from mutagen.id3 import ID3 as mutagen_ID3
from PIL import Image
from kivy.core.window import Window
from kivy.core.image import Image as kvImage
from sounddevice import OutputStream as sdOutputStream
from pedalboard import Pedalboard
from pedalboard.io import AudioFile as pedalboardAudioFile

class AudioFile:
	"""This class is used to load audio file info and audio streams."""
	file_name = None
	_file = None
	image, image_extension = None, None
	title, artist = None, None
	album = None

	channels = None
	sample_rate = None
	sample_total = None
	length_seconds = None

	def __init__(self, path:str, album=None) -> None:
		self.file_name = path
		self._file = pedalboardAudioFile(self.file_name)
		tags = mutagen_ID3(self.file_name)
		# apic is the image in the mp3 tags
		apic = tags.get('APIC:') if tags.get('APIC:') else None
		
		#if the mp3 doesn't have an image loads a transparent black image
		if apic:
			self.image_extension = apic.mime.replace('image/', '')
			self.image = Image.open(BytesIO(apic.data))
		else:
			self.image_extension = 'png'
			self.image = Image.new(mode='RGBA', size=(400,400), color=(10,10,10,127))
		self.title = tags.get('TIT2').text[0] if tags.get('TIT2') else None
		self.artist = tags.get('TPE1').text[0] if tags.get('TPE1') else None
		
		if album:
			self.album = album
		else:
			self.album = None

		# get frame info for progress callbacks and displaying
		#playback_info = mutagen_MP3(self.file_name).info
		self.sample_rate = self._file.samplerate
		self.channels = self._file.num_channels
		self.length_seconds = int(self._file.duration)
		self.sample_total = self._file.frames

		# Preload kvImage
		if self.image and self.image_extension:
			data = BytesIO()
			self.image.save(data, format=self.image_extension)
			data.seek(0)
			im = kvImage(BytesIO(data.read()), ext=self.image_extension)
			self.kv_image = im.texture

	def get_audio(self, pb:Pedalboard = None) -> sdOutputStream:
		"""Returns the full audio numpy array, A pedalboard is optional"""
		if pb:
			return pb(self.get_audio(), self.sample_rate)
		return self._file.read(self.sample_total).T

	def get_frame_volume(self) -> int:
		"""Gets the total number of audio frames this audio file has"""
		return self.sample_total

	def get_image(self) -> Tuple[Image.Image, str]:
		"""Returns the PIL image and the file extension of it in a tuple"""
		return (self.image, self.image_extension)

	def get_image_kv(self) -> kvImage:
		"""Returns the KV image"""
		return self.kv_image

	def __repr__(self) -> str:
		return f'{self.title} - {self.artist} [{self.album}]'

	def close(self) -> None:
		"""Closes the file safely"""
		self._file.close()
		
if __name__ == '__main__':
	# TEST
	
	test = AudioFile('audio/02. It\'s So Creamy.mp3')
	print(test.channels)
	print(test.sample_rate)
	print(test.sample_total)
	print(test.length_seconds)
