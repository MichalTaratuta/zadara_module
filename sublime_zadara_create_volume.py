#!/usr/bin/python

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
		if v['message']:
			return False, False, {"status": v['status'], "message": v['message'], "crap": data}
		else:
			return True, True, {"created": v['vol_name'], "data": data}

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
		module.fail_json(msg="Error deleting repo", meta=result)
if __name__ == '__main__':
	main()	
