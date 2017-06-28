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

api_url = "http://10.221.49.1"

def create_volume(data):
	api_key = data['zadara_auth_key']

	del data['state']
	del data['zadara_auth_key']
	del data['vpsa_address']

	headers = {
		"Content-Type": "application/json",
		"X-Access-Key": "{}" . format(api_key)
	}
	url = "{}{}" . format(api_url, '/api/volumes.json')
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

def main():
	fields = {
		"zadara_auth_key": {"required": True, "type": "str"},
		"vpsa_address": {"required": True, "type": "str"},
		"name": {"required": True, "type": "str"},
		"capacity": {"required": True, "type": "str"},
		"block": {"required": True, "type": "str"},
		"pool": {"required": True, "type": "str"},
		"state": {
			"default": "present",
			"choices": ['present', 'absent'],
			"type": "str"
		},
	}

	choice_map = {
		"present": create_volume,
		#"absent": delete_volume,
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
