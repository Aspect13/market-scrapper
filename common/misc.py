from pathlib import Path
import functools


def pathify(folder_path):
	def decorated_path(func):
		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			try:
				file_name = func(*args, **kwargs)
			except KeyError:
				print(f'No cache for url: {args[0]}')
				return None
			return Path.joinpath(folder_path, file_name)
		return wrapper
	return decorated_path

