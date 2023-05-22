from typing import Callable
from sounddevice import OutputStream as sdOutputStream
from AudioLibrary import AudioLibrary
from AudioFile import AudioFile
from AudioAlbum import AudioAlbum
class AudioHandler:
	"""Class can load a singlular audio stream and play/pause it"""
	playing = False

	audio_library = AudioLibrary()

	audio_queue = []
	current_track = None # Current track is a reference to the AudioFile object
	current_stream = None # Current track Stream is a reference to just the stream
	current_track_audio = None # Current track audio numpy array
	_current_track_position = 0
	current_library_max_length = 0

	_current_frame, _frame_max = 0, 0

	progress_callback = None
	change_callback = None


	def __init__(self) -> None:
		self.audio_library.build()

	def _check_track_position_valid(self, new_position: int) -> bool:
		if self.current_library_max_length > 1 and 0 < new_position <= self.current_library_max_length:
			return True
		print(f'audio library position out of bounds [0 - {self.current_library_max_length}] -> {new_position}')
		return False

	def _finished_callback(self) -> None:
		pass
		#self.close()
		#self.go_to_next_track()

	def change_track_to(self, new_position: int) -> None:
		"""Changes the track position without loading it"""
		if self._check_track_position_valid(new_position):
			self._current_track_position = new_position

	def create_stream(self, audio_file:AudioFile) -> sdOutputStream:
		"""Casts the current loaded AudioFile in to a SoundDevice stream"""
		return sdOutputStream(
				samplerate=audio_file.sample_rate,
				channels=audio_file.channels, 
				callback=self._internal_callback,
				finished_callback=self._finished_callback,
				blocksize=1024)

	def _internal_callback(self, outdata, frames, time, status) -> None:
		"""Callback for loading the audio data frames, this should NOT be used outside of this object"""
		#if not self.playing:
		#	return
		outdata[:] = self.current_track_audio[self._current_frame:self._current_frame+frames]
		self._current_frame += frames

	def load_track(self) -> None:
		"""Loads the current track in to memory from _current_track_position
		   Cant load a track if another one is already playing"""
		self.current_track = self.audio_queue[self._current_track_position]
		self._frame_max = self.current_track.get_frame_volume()
		self._current_frame = 0
		self.current_track_audio = self.current_track.get_audio()

		self.current_stream = self.create_stream(self.current_track)

	def pause(self) -> None:
		"""Pause playback"""
		self.current_stream.stop()
		self.playing = False

	def close(self) -> None:
		"""Closes safely"""
		self.current_track.close()

	def play_or_resume(self) -> None:
		"""Plays or resumes the current track loaded, if any"""
		if not self.current_stream:
			return
		self.current_stream.start()
		self.playing = True

	def load_album_to_queue(self, album:AudioAlbum) -> None:
		"""Load an album in the queue if it exists"""
		if album not in self.audio_library:
			raise LookupError(f'Album provided {album} not in library')
		self.audio_queue.extend(album)
		self.current_library_max_length = len(self.audio_queue)
		self.load_track()

	def _switch_track_relative_position(self, new_position:int, callback:Callable=None) -> None:
		"""Switches to a relative spot in queue, helper method for
		go_to_next_track and go_to_previous_track"""
		new_track_position = self._current_track_position + new_position
		if not self._check_track_position_valid(new_track_position):
			return
		self.pause()
		self.change_track_to(new_track_position)
		self.load_track()
		if callback:
			callback()
		self.play_or_resume()

	def go_to_next_track(self, callback:Callable=None) -> None:
		"""Loads next track and plays it"""
		self._switch_track_relative_position(1, callback=callback)

	def go_to_previous_track(self, callback:Callable=None) -> None:
		"""Loads previous track and plays it"""
		self._switch_track_relative_position(-1, callback=callback)

	def get_current_track_image_kv(self):
		"""Returns current track image as KV image object"""
		if not self.audio_queue:
			return None
		return self.audio_queue[self._current_track_position].get_image_kv()

	def clear_queue(self) -> None:
		"""Clears audio queue and pauses"""
		self.pause()
		self.audio_queue = []
		self.current_library_max_length = 0
		self._current_track_position = 0
		self._current_frame = 0

	def set_change_callback(self, callback:Callable) -> None:
		self.change_callback = callback
		
	def set_progress_callback(self, callback:Callable) -> None:
		"""This callback is called when a frame of audio is played. It must take 1 arg"""
		self.progress_callback = callback

	def __del__(self) -> None:
		pass
		#self.close()


if __name__ == '__main__':
	AH = AudioHandler()
	AH.load_album_to_queue(AH.audio_library.get(0))
	AH.play_or_resume()
	AH.close()
