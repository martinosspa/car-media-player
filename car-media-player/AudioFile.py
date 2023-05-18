from miniaudio import stream_file, mp3_get_file_info
from mutagen.id3 import ID3
from io import BytesIO
from PIL import Image
from typing import Generator, Tuple, Optional
from kivy.core.image import Image as kvImage

class AudioFile:
	"""This class is used to load audio file info and audio streams."""

	def __init__(self, path:str, album=None) -> None:
		self.file_name = path
		tags = ID3(self.file_name)
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
		self.info = mp3_get_file_info(self.file_name)
		self._frame_size = self.info.sample_rate
		self._total_frame_count = self.info.num_frames

		# Load the image as a kv object as well to not load 
		# it every time during run time
		if self.image and self.image_extension:
			data = BytesIO()
			self.image.save(data, format=self.image_extension)
			data.seek(0)
			im = kvImage(BytesIO(data.read()), ext=self.image_extension)
			self.kv_image = im.texture



	def get_new_stream(self, seek_to:Optional[int]=0) -> Generator:
		return stream_file(self.file_name, sample_rate=self.info.sample_rate, seek_frame=seek_to)

	def get_frame_volume(self) -> int:
		"""Gets the total number of audio frames this audio file has"""
		return self._total_frame_count

	def get_image(self) -> Tuple[Image.Image, str]:
		"""Returns the PIL image and the file extension of it in a tuple"""
		return (self.image, self.image_extension)

	def get_image_kv(self) -> kvImage:
		"""Returns the KV image"""
		return self.kv_image

	def __repr__(self) -> str:
		return f'{self.title} - {self.artist} [{self.album}]'
