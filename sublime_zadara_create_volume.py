#!/usr/bin/python

DOCUMENTATION = '''
---
module: zadara_volume
short_description: Creates and Removes volumes
'''

EXAMPLES = '''
- name: Create a volume
  zadara_volume:
    zadara_auth_key: "..."
    vpsa_address: "10.10.10.10"
    name: "Hello-World"
    capacity: "50G"
    block: "yes"
    pool: "pool-00000001"
    status: present
  register: result

- name: Delete a volume
  zadara_volume:
    zadara_auth_key: "..."
    vpsa_address: "10.10.10.10"
    name: "Hello-World"
    force: "no"
    state: absent
  register: result
'''

from ansible.module_utils.basic import *
import requests
from zadara_name2id import Zadara_name2id

def create_volume(data):
	if data['connection'] == 'secure':
		api_url_prefix = "https://"
	else:
		api_url_prefix = "http://"

	api_url_suffix = data['vpsa_address']
	api_key = data['zadara_auth_key']
	api_url = "{}{}" . format(api_url_prefix, api_url_suffix)
	api_endpoint = '/api/volumes.json'

	del data['state']
	del data['zadara_auth_key']
	del data['vpsa_address']
	del data['connection']

	headers = {
		"Content-Type": "application/json",
		"X-Access-Key": "{}" . format(api_key)
	}
	url = "{}{}" . format(api_url, api_endpoint)
	result = requests.post(url, json.dumps(data), headers=headers)

	for k,v in result.json().items():
		if v['status'] == 10096:
			result = {"status_code": v['status'], "message": v['message']}
			return False, False, result
		elif v['status'] != 0:
			result = {"status_code": v['status'], "message": v['message']}
			return True, False, result
		else:
			result = {"status": "SUCCESS", "created": v['vol_name']}
			return False, True, result

def delete_volume(data):

	if data['connection'] == 'secure':
		api_url_prefix = "https://"
	else:
		api_url_prefix = "http://"

	# We need to convert the Volume name to an ID
	volume_name = data['name']
	name2id = Zadara_name2id('volumes', volume_name, data['vpsa_address'], data['zadara_auth_key'], api_url_prefix)
	volume_id = name2id.get_object_id(volume_name)

	api_url_suffix = data['vpsa_address']
	api_key = data['zadara_auth_key']
	api_url = "{}{}" . format(api_url_prefix, api_url_suffix)
	api_endpoint = "{}{}{}" . format('/api/volumes/', volume_id, '.json')

	headers = {
		"Content-Type": "application/json",
		"X-Access-Key": "{}" . format(api_key)
	}
	url = "{}{}" . format(api_url, api_endpoint)

	# Checking if the Force value is set
	for k,v in data.items():
		if k == 'force':
			froce_present = True

	if froce_present:
		new_data = {}
		new_data['force'] = data['force']
		result = requests.delete(url, data=json.dumps(new_data), headers=headers)
	else:
		result = requests.delete(url, headers=headers)

	for k,v in result.json().items():
		if v['status'] == 10097:
			result = {"status_code": v['status'], "message": v['message']}
			return False, False, result
		elif v['status'] != 0:
			result = {"status_code": v['status'], "message": v['message']}
			return True, False, result
		else:
			result = {"status": "SUCCESS", "removed": volume_name}
			return False, True, result

def main():
	fields = {
		"zadara_auth_key": {"required": True, "type": "str"},
		"vpsa_address": {"required": True, "type": "str"},
		"name": {"required": True, "type": "str"},
		"capacity": {"required": False, "type": "str"},
		"block": {"required": False, "type": "str"},
		"pool": {"required": False, "type": "str"},
		"force": {"required": False, "type": "str"},
		"connection": {
			"default": "unsecure",
			"choices": ['secure', 'unsecure'],
			"type": "str"
		},
		"state": {
			"default": "present",
			"choices": ['present', 'absent'],
			"type": "str"
		},
	}

	choice_map = {
		"present": create_volume,
		"absent": delete_volume,
	}

	module = AnsibleModule(argument_spec=fields)
	is_error, has_changed, result =  choice_map.get(
		module.params['state'])(module.params)

	if not is_error:
		module.exit_json(changed=has_changed, meta=result)
	else:
		module.fail_json(msg=result)
if __name__ == '__main__':
	main()	
