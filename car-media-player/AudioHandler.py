from miniaudio import PlaybackDevice, stream_with_callbacks
from AudioFile import AudioFile
import os
from typing import Generator


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
		self._current_frame = 0
		self._frame_max = 0
		self.audio_stream = None
		self._queue_next_track = False

	def load_track(self) -> None:
		'''Loads the current track in to memory from current_track_position
		   Cant load a track if another one is already playing'''
		   
		if not self.playing and self.playback_device.running:
			self.playback_device.stop()
		if not 0 <= self.current_track_position < self.current_library_max_length:
			print(f'audio library position out of bounds [{0} - {self.current_library_max_length}] -> {self.current_track_position}')
			return

		self.current_track = self.audio_queue[self.current_track_position]
		self._frame_max = self.current_track.get_frame_volume()
		self._current_frame = 0

		audio_stream = self.current_track.get_new_stream()
		self.audio_stream = stream_with_callbacks(audio_stream,
												lambda frames: self.progress_audio_callback(frames),
												lambda: self.end_audio_callback())
		next(self.audio_stream)

	def play_or_resume(self) -> None:
		'''Plays the track at the current_track_position'''
		print(f'current position: {self.current_track_position}')
		if not self.audio_stream and not self.playback_device.running:
			self.load_track()
		print(self.playback_device.running)
		self.playback_device.start(self.audio_stream)
		self.playing = True
		while self.playing:
			pass
		else:
			self.go_to_next_track()


		

	def progress_audio_callback(self, frame_count: int) -> None:
		print(f'{self._current_frame} / {self._frame_max}')
		self._current_frame += frame_count

	def end_audio_callback(self) -> None:
		'''This raises a flag playing to end the while loop hanging the program so a weird race error is not raised'''
		self.playing = False

	def close(self) -> None:
		'''This closes the audio handler safely'''
		self.playback_device.stop()
		self.playing = False
		self.audio_stream = None
		self.playback_device.close()

	def pause(self) -> None:
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
	#input('enter to continue')
	AH.close()
