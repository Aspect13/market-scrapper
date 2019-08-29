import requests
from pathlib import Path

from pip._internal.utils.misc import cached_property

from settings import ROOT_DIR, IMG_CACHE_FOLDER_RELATIVE
from common.misc import add_schema
from syncronous.utils import get_unique_file_name
from common.models import ProductModel, Session
import json

# def get_name_from_img_url(img_url):
# 	name = None
# 	for i in reversed(img_url.split('/')):
# 		if '.' in i:
# 			name = i
# 			return name.split('.')[0]
# 	if not name:
# 		name = img_url.replace(r'/', '__')
#
# 	return name


class Image:
	SESSION = None
	# FOLDER_DEFAULT = Path(ROOT_DIR, IMG_CACHE_FOLDER_RELATIVE)
	FOLDER_DEFAULT = Path(ROOT_DIR, 'tmp', 'img')

	def __init__(self, url):
		self.url = add_schema(url)
		self.extension = self.get_extension_from_url(self.url)
		# self.local_path = None

	@cached_property
	def exists(self):

		return json.load(open(Path(ROOT_DIR, 'tmp', 'tmp.json'), 'r')).get(self.url)
		try:
			return self.SESSION.query(ProductModel.img_filename).filter(ProductModel.img_url == self.url).first()
		except AttributeError:
			Image.SESSION = Session()
			return self.SESSION.query(ProductModel.img_filename).filter(ProductModel.img_url == self.url).first()

	@staticmethod
	def get_extension_from_url(url, default='jpg'):
		d = {
			'.jpeg': 'jpeg',
			'.png': 'png',
			'.gif': 'gif'
		}
		for k, v in d.items():
			if k in url:
				return v
		return default

	def download(self, destination_folder=FOLDER_DEFAULT):
		if self.exists:
			if destination_folder != self.FOLDER_DEFAULT:
				import shutil
				shutil.copy(self.FOLDER_DEFAULT, destination_folder)
			return self.exists

		file_name = get_unique_file_name(destination_folder, self.extension)

		print('Downloading...')
		response = requests.get(self.url)
		print('Downloading...COMPLETE')

		with open(Path(destination_folder, file_name), 'wb') as out:
			out.write(response.content)

		d = json.load(open(Path(ROOT_DIR, 'tmp', 'tmp.json'), 'r'))
		if destination_folder != self.FOLDER_DEFAULT:
			d.update({self.url: str(Path(destination_folder, file_name))})
			print(d)
			json.dump(open(Path(ROOT_DIR, 'tmp', 'tmp.json'), 'w'), d)
			return Path(destination_folder, file_name)

		d.update({self.url: file_name})
		print(d)
		json.dump(open(Path(ROOT_DIR, 'tmp', 'tmp.json'), 'w'), d)
		return file_name

	def __repr__(self):
		d = self.__dict__
		d['exists'] = self.exists
		return '''Image
		url: {url},
		ext: {extension},
		exists: {exists}
		'''.format(**d)
