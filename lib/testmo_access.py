import json
from typing import Callable, Any
from email.policy import default

from lib.dict_util import dict_to_namespace
from lib.rest_request import RestRequest
from schema import testmo_project_info_reply


testmo_result_status = dict_to_namespace({
    "Untested": 1,
    "Passed": 2,
    "Failed": 3,
    "Retest": 4,
    "Blocked": 5,
    "Skipped": 6
})
testmo_result_status_names = {v: k for k, v in vars(testmo_result_status).items()}

testmo_result_colors = dict_to_namespace({
    "Untested": None,
    "Passed": '36ab51',
    "Failed": 'f44b25',
    "Retest": 'ffaa00',
    "Blocked": '9a9b9c',
    "Skipped": '16abc5'
})
testmo_result_colors_by_code = {
	getattr(testmo_result_status, k): getattr(testmo_result_colors, k) for k in vars(testmo_result_status)
}

testmo_config = None
testmo_config_file = 'testmo_config.json'

try:
	with open(testmo_config_file, 'r') as f:
		testmo_config = json.load(f)

	testmo_credentials = testmo_config['token']
	testmo = RestRequest(
		base_url=testmo_config['url'],
		headers={
			'accept': 'application/json',
			'Authorization': f'Bearer {testmo_credentials}'
		}
	)
	testmo_user = testmo.copy(endpoint='user')
	testmo_test_project = testmo.copy(endpoint='projects/44')
	testmo_test_runs = testmo.copy(endpoint='projects/44/runs')
	testmo_test_run_ilja = testmo.copy(endpoint='runs/455/results')

except Exception:
	testmo_credentials = None
	testmo = None
	testmo_config = {}
	testmo_user = None
	testmo_test_project = None
	testmo_test_runs = None
	testmo_test_run_ilja = None

# /api/v1/projects/{project_id}/runs
# /api/v1/runs/{run_id}/results


def testmo_projects_request(base_request=testmo):
	result = base_request.copy(endpoint='projects')
	return result


def testmo_project_request(project_id, base_request=testmo):
	result = testmo_projects_request(base_request=base_request).extend_endpoint(str(project_id))
	return result


def testmo_project_runs_request(project_id, base_request=testmo):
	result = testmo_project_request(project_id, base_request=base_request).extend_endpoint('runs')
	return result


def testmo_project_run_request(run_id, base_request=testmo):
	result = base_request.copy(endpoint='runs').extend_endpoint(str(run_id))
	return result


def testmo_project_run_results_request(run_id, base_request=testmo):
	result = testmo_project_run_request(run_id, base_request=base_request).extend_endpoint('results')
	return result


# def testmo_make_request(app_config: dict[str, object], endpoint=None):
# 	result = RestRequest(
# 		base_url=app_config['testmo_url'],
# 		headers={
# 			'accept': 'application/json',
# 			'Authorization': f'Bearer {app_config["testmo_password"]}'
# 		}
# 	)
#
# 	if endpoint is not None:
# 		return result.copy(endpoint=endpoint)
# 	else:
# 		return result


def testmo_collect(rest_request: RestRequest, convert_to: Callable[[dict[str, Any]], Any] = None):
	current_request = rest_request
	result = []
	while True:
		reply = current_request.get()
		result.extend(reply['result'])
		if reply['page'] == reply['last_page']:
			break

		current_request = current_request.copy(page=reply['next_page'])

	if convert_to is not None:
		result = [convert_to(entry) for entry in result]

	return result


if __name__ == '__main__':
	def main():
		test8 = testmo_projects_request()
		# test2 = testmo_test_runs.get()
		# test4 = testmo_collect(testmo_test_runs)
		test6 = testmo_project_request(44).get()
		x = testmo_project_info_reply.from_data(test6)
		test7 = testmo_collect(testmo_project_runs_request(44))
		# test3 = testmo_test_run_ilja.get()
		test5 = testmo_collect(testmo_test_run_ilja)
		# test1 = testmo_user.get()
		pass

	main()
