#from AudioFile import AudioFile
from AudioAlbum import AudioAlbum
import os
from typing import List
from mutagen.id3 import ID3
from PIL import Image
from io import BytesIO

class AudioLibrary:
	"""Class that contains AudioAlbums. Is iterable"""
	_AUDIO_FILE_EXTENSIONS = ['.mp3']
	albums = []

	def build(self) -> None:
		path = 'audio/'
		for file_name in os.listdir(path):
			audio_file_name = os.path.join(path, file_name)

			if not os.path.isfile(audio_file_name):
				continue

			# checks if the file that was found has a supported format
			if not os.path.splitext(audio_file_name)[1] in self._AUDIO_FILE_EXTENSIONS:
				continue

			# Load mp3 tags
			tags = ID3(audio_file_name)
			apic = tags.get('APIC:') if tags.get('APIC:') else None
			album_title = tags.get('TALB').text[0] if tags.get('TALB') else None
			album_artist = tags.get('TPE1').text[0] if tags.get('TPE1') else None
			
			# apic is the data for the image
			# it gets loaded in to a PIL image
			if apic: 
				image_extension = apic.mime.replace('image/', '')
				image = Image.open(BytesIO(apic.data))
			else:
				image_extension = 'png'
				image = Image.new(mode='RGBA', size=(400,400), color=(10,10,10,127))
			
			new_potential_album = AudioAlbum(image=image, 
											 image_extension=image_extension, 
										 	 name=album_title, 
										 	 artist=album_artist)

			# check if the album in the current iterating audio file exists
			if new_potential_album in self.albums:
				album_index = self.albums.index(new_potential_album)
			else:
				self.albums.append(new_potential_album)
				album_index = len(self.albums) - 1

			self.albums[album_index].add_audio_file(audio_file_name)

	def get_albums(self) -> List[AudioAlbum]:
		"""Get all albums"""
		return self.albums

	def get(self, pos:int) -> AudioAlbum:
		"""Get an album by position"""
		return self.albums[pos]

	def __iter__(self):
		self._index = 0
		return self

	def __next__(self):
		if self._index < len(self.albums):
			r = self.albums[self._index]
			self._index += 1
			return r
		else:
			raise StopIteration

if __name__ == '__main__':
	# testing
	AL = AudioLibrary()
	AL.build()
	for album in AL.albums:
		print(f'-- {album} -- ')
		print(album.image)
		#for song in album:
		#	print(song)
	print(AL.albums)