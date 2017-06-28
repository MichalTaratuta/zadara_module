import requests

class Zadara_name2id():
	def __init__(self, object_type, object_name, vpsa_address, zadara_auth_key, connection):
		self.object_type = object_type
		self.object_name = object_name
		self.vpsa_address = vpsa_address
		self.zadara_auth_key = zadara_auth_key
		self.connection = connection

		api_url = "{}{}{}" . format(connection, vpsa_address, '/api/')
		url = "{}{}{}" . format(api_url, object_type, '.json')
		headers = {'X-Access-Key': zadara_auth_key}

		self.r = requests.get(url, headers=headers)

	def process_response(self):
		data = self.r.json()
		response_list = []
		for k, v in data.items():
			response_list.append(v)
		return response_list

	def get_objects_list(self):
		response_list = self.process_response()
		for i in response_list:
			return i[self.object_type]

	def get_object_names(self):
		object_list = self.get_objects_list()
		objects_dic = {}
		for i in object_list:
			objects_dic[i.get('display_name')] = i.get('name')
		return objects_dic

	def get_object_id(self, object_name):
		object_ids = self.get_object_names()
		if object_name in object_ids:
			return object_ids[self.object_name]
		else:
			raise KeyError()