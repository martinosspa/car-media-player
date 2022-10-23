from miniaudio import stream_file, mp3_get_file_info, stream_with_callbacks
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from io import BytesIO
from PIL import Image
from copy import deepcopy
from typing import Generator
class AudioFile():
	'''This class is used to load audio file info and audio streams in to memory'''
	def __init__(self, path:str):
		self.file_name = path
		tags = ID3(self.file_name)
		pict = tags.get('APIC:').data if tags.get('APIC:') else None
		self.image = Image.open(BytesIO(pict)) if pict else None
		self.title = tags.get('TIT2').text[0] if tags.get('TIT2') else None
		self.album = tags.get('TALB').text[0] if tags.get('TALB') else None
		self.artist = tags.get('TPE1').text[0] if tags.get('TPE1') else None

		# get frame info for progress callbacks and displaying
		info = mp3_get_file_info(self.file_name)
		self._frame_size = info.sample_rate
		self._total_frame_count = info.num_frames
		print(self._frame_size, self._total_frame_count)
		
		self.original_stream = stream_file(self.file_name)
		#next(self.original_stream)
		self.mutable_stream = self.original_stream



	def get_new_stream(self) -> Generator:
		return self.mutable_stream

	def get_frame_volume(self) -> int:
		'''Gets the total number of audio frames this audio file has'''
		return self._total_frame_count

	def __repr__(self) -> str:
		return f'{self.title} - {self.artist} [{self.album}]'
