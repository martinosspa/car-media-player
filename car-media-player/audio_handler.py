from miniaudio import PlaybackDevice, stream_file
from mutagen.mp3 import MP3
from mutagen.id3 import ID3


from io import BytesIO
from PIL import Image



class AudioHandler():
	'''This class can load a single audio file, play and/or pause it'''
	def __init__(self):
		self.playing = False
		self.playback_device = PlaybackDevice()

	# to be removed
	def load_single_file(self, file_name: str) -> None:
		self.file_name = file_name
		tags = ID3(self.file_name)
		pict = tags.get('APIC:').data
		self.image = Image.open(BytesIO(pict))
		self.title = tags.get('TIT2').text[0]
		self.album = tags.get('TALB').text[0]
		self.artist = tags.get('TPE1').text[0]
		self.stream = stream_file(file_name)
		next(self.stream)
		
	
	def play_or_resume(self) -> None:
		if not self.playing:
			self.playback_device.start(self.stream)
			self.playing = True


	def close(self) -> None:
		self.playback_device.stop()
		self.playing = False
		self.stream = None
		self.playback_device.close()


	def pause(self) -> None:
		if self.playing:
			self.playback_device.stop()
			self.playing = False



if __name__ == '__main__':
	# this is for testing purposes
	from time import sleep
	AH = AudioHandler()
	AH.load_single_file('audio/3. Lonely Driving.mp3')
	AH.play_or_resume()
	sleep(10)
	AH.pause()
	sleep(3)
	AH.play_or_resume()
	sleep(5)
	AH.close()
