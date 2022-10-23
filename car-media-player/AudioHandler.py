from miniaudio import PlaybackDevice, stream_with_callbacks
from AudioFile import AudioFile
import os


def stream_end_callback() -> None:
    print("\nSource stream ended!")


def stream_progress_callback(framecount: int) -> None:
    print(framecount, ",", end="", flush=True)

class AudioHandler():
	'''This class can load a single audio file, play and/or pause it'''
	def __init__(self):
		self._AUDIO_FILE_EXTENSIONS = ['.mp3']
		self.playing = False
		self.directory = 'audio'
		self.playback_device = PlaybackDevice()
		self.audio_queue = []
		self.current_track = None
		self.current_track_position = 0
		self.current_library_max_length = 0
	
	def play_or_resume(self) -> None:
		if not self.playing:
			if 0 <= self.current_track_position and self.current_track_position < self.current_library_max_length:
				self.current_track = self.audio_queue[self.current_track_position]

				self.call_back_stream = stream_with_callbacks(self.current_track.get_new_stream, stream_progress_callback, stream_end_callback)
				next(self.call_back_stream)
				self.playback_device.start(self.call_back_stream)
				#self.current_track.image.show()
				self.playing = True
			else:
				# debug
				print(f'audio library position out of bounds [{0} - {self.current_library_max_length}] -> {self.current_track_position}')
			

	def close(self) -> None:
		self.playback_device.stop()
		self.playing = False
		self.stream = None
		self.playback_device.close()


	def pause(self) -> None:
		if self.playing:
			self.playback_device.stop()
			self.playing = False

	def go_to_next_track(self) -> None:
		self.pause()
		self.current_track_position += 1
		self.play_or_resume()

	def go_to_previous_track(self) -> None:
		self.pause()
		self.current_track_position -= 1
		self.play_or_resume()


	def load_first_found_file_and_queue(self) -> None:
		for file_name in os.listdir(self.directory):
			audio_file_name = os.path.join(self.directory, file_name)
			if os.path.isfile(audio_file_name):
				if os.path.splitext(audio_file_name)[1] in self._AUDIO_FILE_EXTENSIONS:
					self.audio_queue.append(AudioFile(audio_file_name))
		self.current_library_max_length = len(self.audio_queue)


if __name__ == '__main__':
	# this is for testing purposes
	from time import sleep
	AH = AudioHandler()
	AH.load_first_found_file_and_queue()
	print(AH.audio_queue)
	AH.play_or_resume()
	sleep(10)
	AH.go_to_next_track()
	sleep(5)
	AH.close()