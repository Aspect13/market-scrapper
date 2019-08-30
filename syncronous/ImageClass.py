import shutil

import requests
from pathlib import Path


from settings import ROOT_DIR, IMG_CACHE_FOLDER_RELATIVE
from common.misc import add_schema
from syncronous.utils import get_unique_file_name
from common.models import ImageModel, ConnectedToModel


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


class Image(ConnectedToModel):
	FOLDER_DEFAULT = Path(ROOT_DIR, IMG_CACHE_FOLDER_RELATIVE)
	# FOLDER_DEFAULT = Path(ROOT_DIR, 'tmp', 'img')

	def __init__(self, url):
		super().__init__(ImageModel)
		self.__db_instance = None
		self.url = add_schema(url)
		self.extension = self.get_extension_from_url(self.url)
		# self.db_instance = self.MODEL(url=self.url)
		# self.local_path = None

	def commit(self):
		self.session.add(self.db_instance)
		self.session.commit()

	@property
	def exists(self):
		return bool(self.db_instance.id)

	@property
	def db_instance(self):
		if self.__db_instance:
			return self.__db_instance
		self.__db_instance = self.session.query(self.model).filter(
			self.model.url == self.url
		).first()
		if not self.__db_instance:
			self.__db_instance = self.model(url=self.url)
		return self.__db_instance

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

	def copy_to(self, destination):
		shutil.copy(Path(self.FOLDER_DEFAULT, self.db_instance.filename), Path(destination, self.db_instance.filename))

	def download(self, destination_folder=FOLDER_DEFAULT):
		if self.db_instance.filename:
			if destination_folder != self.FOLDER_DEFAULT:
				self.copy_to(destination_folder)
			return self.db_instance.filename

		file_name = get_unique_file_name(destination_folder, self.extension)

		print('Downloading...')
		response = requests.get(self.url)
		print('Downloading...COMPLETE')

		with open(Path(self.FOLDER_DEFAULT, file_name), 'wb') as out:
			out.write(response.content)

		self.db_instance.filename = file_name
		self.commit()

		if destination_folder != self.FOLDER_DEFAULT:
			self.copy_to(destination_folder)

		return file_name

	def __repr__(self):
		d = self.__dict__
		return '''Image
		url: {url},
		ext: {extension},
		'''.format(**d)
