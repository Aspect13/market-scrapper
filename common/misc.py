import json
import re
from pathlib import Path
import functools

from settings import CACHE_DICT_PATH


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


def get_cache_dict():
	try:
		return json.load(open(CACHE_DICT_PATH, 'r'))
	except FileNotFoundError:
		with open(CACHE_DICT_PATH, 'w') as f:
			f.write('{}')
	return {}


