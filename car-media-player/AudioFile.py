from miniaudio import stream_file, mp3_get_file_info, stream_with_callbacks, read_file
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from io import BytesIO
from PIL import Image
from copy import deepcopy, copy
from typing import Generator, Tuple
class AudioFile:
	"""This class is used to load audio file info and audio streams"""

	def __init__(self, path:str) -> None:
		self.file_name = path
		tags = ID3(self.file_name)
		apic = tags.get('APIC:') if tags.get('APIC:') else None
		pict = apic.data if apic else None
		if apic:

			self.image_extension = apic.mime.replace('image/', '')
		else:
			self.image_extension = None
		self.image = Image.open(BytesIO(pict)) if pict else None
		self.title = tags.get('TIT2').text[0] if tags.get('TIT2') else None
		self.album = tags.get('TALB').text[0] if tags.get('TALB') else None
		self.artist = tags.get('TPE1').text[0] if tags.get('TPE1') else None

		# get frame info for progress callbacks and displaying
		self.info = mp3_get_file_info(self.file_name)
		self._frame_size = self.info.sample_rate
		self._total_frame_count = self.info.num_frames
		
		

	def get_new_stream(self) -> Generator:
		return stream_file(self.file_name, sample_rate=self.info.sample_rate)

	def get_frame_volume(self) -> int:
		"""Gets the total number of audio frames this audio file has"""
		return self._total_frame_count

	def get_image(self) -> Tuple[Image.Image, str]:
		"""Returns the PIL image and the file extension of it in a tuple"""
		return (self.image, self.image_extension)

	def __repr__(self) -> str:
		return f'{self.title} - {self.artist} [{self.album}]'
