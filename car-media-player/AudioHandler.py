from miniaudio import PlaybackDevice, stream_with_callbacks
from AudioFile import AudioFile
from typing import Generator, Tuple, Optional, Callable
import PIL
from threading import Thread
import time

from AudioAlbum import AudioAlbum
from AudioLibrary import AudioLibrary

class AudioHandler(Thread):
	"""This class can load a single audio file, play and/or pause it"""

	# General flags / options
	playing = False # If a track is currently playing
	running = False # If the thread should be running
	_queue_next_track = False #Queue next track on next check

	# Audio Library
	audio_library = AudioLibrary()

	# Audio track queue and info
	audio_queue = []
	audio_stream = None 
	current_track = None 
	_current_track_position = 0
	current_library_max_length = 0

	# Audio frame info
	_current_frame = 0 # Current frame number the Playback Device is at
	_frame_max = 0
	_current_progress = 0 # Float 0 -> 1, 0.5 meaning the current audio track is at 50%
		
	# Callbacks
	progress_callback = None
	change_callback = None


	def __init__(self):
		Thread.__init__(self)
		self.playback_device = PlaybackDevice()

	def start(self) -> None:
		"""Starts the Audio Handler thread and builds the library"""
		super().start()
		self.running = True
		self.audio_library.build()

	def _check_track_position_valid(self, new_position: int) -> bool:
		"""Check if a new given track position is valid"""
		if self.current_library_max_length > 0 and 0 <= new_position <= self.current_library_max_length:
			return True
		print(f'audio library position out of bounds [{0} - {self.current_library_max_length}] -> {new_position}')
		return False
		
	def change_track_to(self, new_position: int) -> None:
		"""Changes the track position without loading it"""
		self._current_track_position = new_position

	def load_track(self, seek_to:Optional[int] = 0) -> None:
		"""Loads the current track in to memory from _current_track_position
		   Cant load a track if another one is already playing"""
		self.current_track = self.audio_queue[self._current_track_position]
		self._frame_max = self.current_track.get_frame_volume()
		self._current_frame = 0

		self.audio_stream = stream_with_callbacks(self.current_track.get_new_stream(seek_to=seek_to),
												progress_callback=lambda frames: self._progress_audio_callback(frames),
												end_callback=lambda: self._set_next_track())
		next(self.audio_stream)

		#This is used to load correct sample_rate in to Playback Device
		if not self.current_track.info.sample_rate == self.playback_device.sample_rate:
			self.playback_device = PlaybackDevice(sample_rate=self.current_track.info.sample_rate)

		if seek_to:
			self._current_frame = seek_to

	def play_or_resume(self) -> None:
		"""Plays the track at the _current_track_position"""
		if not self.audio_stream:
			return
		self.playback_device.start(self.audio_stream)
		self.playing = True
		
	def set_change_callback(self, callback:Callable) -> None:
		self.change_callback = callback
		
	def set_progress_callback(self, callback:Callable) -> None:
		"""This callback is called when a frame of audio is played. It must take 1 arg"""
		self.progress_callback = callback

	def _set_next_track(self) -> None:
		self._queue_next_track = True

	def _progress_audio_callback(self, frame_count: int) -> None:
		"""Private callback method to update self progress, current frame, and call the progress callback if it's set"""
		self._current_frame += frame_count
		self._current_progress = self._current_frame/self._frame_max

		if self.progress_callback:
			self.progress_callback(self._current_progress)


	def close(self) -> bool:
		"""This closes the audio handler safely"""
		self.playback_device.stop()
		self.playing = False
		self.audio_stream = None
		self.running = False
		self.playback_device.close()
		return False

	def pause(self) -> None:
		"""Pause playback"""
		self.playback_device.stop()
		self.playing = False
		
	def go_to_next_track(self, callback:Optional[Callable] = None) -> None:
		"""Loads and plays next track"""
		new_track_position = self._current_track_position + 1
		if not self._check_track_position_valid(new_track_position):
			return
		self.pause()
		self.change_track_to(new_track_position)
		self.load_track()
		if callback:
			callback()

		self.play_or_resume()

	def go_to_previous_track(self, callback:Optional[Callable] = None) -> None:
		"""Loads and plays previous track"""
		new_track_position = self._current_track_position - 1
		if not self._check_track_position_valid(new_track_position):
			return
		self.pause()
		self.change_track_to(new_track_position)
		self.load_track()
		if callback:
			callback()
		self.play_or_resume()

	def load_album_to_queue(self, album:AudioAlbum) -> None:
		"""Loads a certain AudioAlbum from the audio library in to the queue"""
		if not album:
			return
		if album not in self.audio_library:
			raise LookupError(f'Album provided ({album}) not in Audio Library')
		self.audio_queue.extend(album)
		self.current_library_max_length = len(self.audio_queue) - 1
		self.load_track()
		
	def get_current_track_image(self) -> Tuple[PIL.Image.Image, str]:
		"""Returns current track image as PIL image and it's file extension as a tuple"""
		if not self.audio_queue:
			return []
		return self.audio_queue[self._current_track_position].get_image()

	def clear_queue(self) -> None:
		"""Clears audio queue and pauses"""
		self.pause()
		self.audio_stream = None
		self.audio_queue = []
		self.current_library_max_length = 0
		self._current_track_position = 0


	def run(self) -> None:
		"""This shouldn't be called from the user, but from parent thread class since this is a threaded class"""
		while self.running:
			if self._queue_next_track:
				self._queue_next_track = False
				self.go_to_next_track(self.change_callback)
			time.sleep(0.01)
	
	def __del__(self) -> None:
		self.close()

	def seek_to_percentage(self, value: float) -> None:
		self.pause()
		seek_frame_value = int(value * self._frame_max)
		self.load_track(seek_to=seek_frame_value)
		self.play_or_resume()