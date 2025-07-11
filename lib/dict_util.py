from types import SimpleNamespace


def dict_from(**kwargs):
	return kwargs


def dict_to_namespace(d):
	if isinstance(d, dict):
		return SimpleNamespace(**{k: dict_to_namespace(v) for k, v in d.items()})
	elif isinstance(d, list):
		return [dict_to_namespace(item) for item in d]
	else:
		return d


def dict_entries(the_dic, *args: str):
	result = {k: v for k, v in the_dic.items() if k in args}
	return result

