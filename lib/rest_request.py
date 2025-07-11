import copy
import json

import requests
from urllib.parse import urlencode, urljoin, urlparse, parse_qs
import os
from typing import Union, Optional


class RestRequest:
	class Error(Exception):
		pass

	def __init__(
			self,
			auth=None,
			base_url="",
			endpoint="",
			params=None,
			body=None,
			headers=None,
			expect_json=True,
			**kwargs
	):
		"""
		Initialize a RestRequest object with optional authentication, base URL, endpoint,
		query parameters, request body, headers, and whether to expect a JSON response, in which case it gets parsed.
		"""
		self.auth = auth
		self.base_url = base_url.rstrip("/") if base_url else ""
		self.endpoint = endpoint.lstrip("/") if endpoint else ""
		self.params = params.copy() if params else {}
		self.body = body or {}
		self.headers = headers or {}
		self.expect_json = expect_json

		# Merge keyword arguments into params (overwriting existing keys)
		self.params.update(kwargs)

	def set_params(self, params=None, **kwargs) -> "RestRequest":
		"""
		Set or update query parameters.

		Args:
			params (dict, optional): Dictionary of parameters to set.
			**kwargs: Additional parameters to add or overwrite.

		Returns:
			RestRequest: The modified request object.
		"""
		self.params = params.copy() if params else {}
		self.params.update(kwargs)
		return self

	def modify(self, **kwargs) -> "RestRequest":
		"""
		Modify attributes or query parameters of the request.

		Args:
			**kwargs: Key-value pairs of attributes or parameters to modify.

		Returns:
			RestRequest: The modified request object.
		"""
		for k, v in kwargs.items():
			if hasattr(self, k):
				setattr(self, k, v)
			else:
				self.params[k] = v
		return self

	def merge(self, rest_request: Union["RestRequest", dict]) -> "RestRequest":
		"""
		Merge the params of 2 requests.
		Args:
			rest_request: provides params to merge with. Overwrites existing params from self.
						  If rest_request is a RestRequest, only the params are updated.
		Returns:
			The merge result.
		"""
		params = rest_request.params if isinstance(rest_request, RestRequest) else rest_request
		result = self.copy(**params)
		return result

	def get_full_url(self):
		"""
		Construct the full URL with parameters.

		Returns:
			str: Full URL including query string.
		"""
		url = urljoin(self.base_url + "/", self.endpoint)
		if self.params:
			query_string = urlencode(self.params)
			url = f"{url}?{query_string}"
		return url

	def extend_endpoint(self, extension: Union[str, list]) -> "RestRequest":
		"""
		Extend the current endpoint with additional path segments.

		Args:
			extension (Union[str, list]): Path segment(s) to append to the endpoint.

		Returns:
			RestRequest: The modified request object.
		"""
		if isinstance(extension, list):
			extension = "/".join([str(e) for e in extension])
		self.endpoint = f'{str(self.endpoint).rstrip("/")}/{str(extension).lstrip("/" )}'
		return self

	def send(self, method, **kwargs):
		"""
		Send an HTTP request with the given method.

		Args:
			method (str): HTTP method (e.g., 'GET', 'POST').
			**kwargs: Optional modifications to apply before sending.

		Returns:
			requests.Response or dict: Parsed JSON response or raw response.

		Raises:
			FileNotFoundError: If specified file for body is not found.
			ValueError: If the response status code is not 200.
		"""
		this = self.copy(**kwargs) if len(kwargs) > 0 else self
		url = this.get_full_url()
		method = method.upper()

		data = None
		json_data = None

		if isinstance(this.body, str) and this.body.startswith("@") and len(this.body.split()) == 1:
			file_path = this.body[1:]
			if not os.path.isfile(file_path):
				raise RestRequest.Error(f"Body file '{file_path}' not found.")

			with open(file_path, 'r', encoding='utf-8') as f:
				data = f.read()

		elif method in ("POST", "PUT"):
			json_data = this.body

		response = requests.request(
			method=method,
			auth=this.auth,
			url=url,
			headers=this.headers,
			data=data,
			json=json_data
		)

		if response.status_code > 299:
			if hasattr(response, 'get'):
				error = response.get("text", "(no text)")
			else:
				error = response.text
			raise RestRequest.Error(f'Error Response: {response}: {error}')

		return response if not self.expect_json else json.loads(response.text) if len(response.text) > 0 else True

	def get(self, **kwargs):
		"""
		Send a GET request.

		Args:
			**kwargs: Optional modifications to apply before sending.

		Returns:
			requests.Response or dict: Parsed JSON or raw response.
		"""
		return self.send('GET', **kwargs)

	def put(self, **kwargs):
		return self.send('PUT', **kwargs)

	def post(self, **kwargs):
		return self.send('POST', **kwargs)

	def copy(self,  **kwargs) -> "RestRequest":
		"""
		Create a deep copy of the request and apply modifications.

		Args:
			**kwargs: Attributes or parameters to modify in the copy.

		Returns:
			RestRequest: The copied and modified request object.
		"""
		result = copy.deepcopy(self)
		return result.modify(**kwargs)

	def __repr__(self):
		return (f"ApiRequest(base_url='{self.base_url}', endpoint='{self.endpoint}', "
				f"params={self.params}, body={self.body}, headers={self.headers})")

	@classmethod
	def from_url(
			cls,
			base_url: Union[str, "RestRequest"],
			full_url: Union[str, "RestRequest"],
			template: Optional["RestRequest"] = None
	) -> "RestRequest":
		"""
		Create a RestRequest object from a full URL and a base URL.

		Args:
			base_url (Union[str, RestRequest]): Base URL or an existing RestRequest.
			full_url (Union[str, RestRequest]): Full URL to parse.
			template (Optional[RestRequest]): Template request to copy.

		Returns:
			RestRequest: Constructed request object with parsed endpoint and parameters.

		Raises:
			ValueError: If full_url does not start with base_url.
		"""
		if isinstance(full_url, RestRequest):
			return full_url

		if template is None:
			template = cls()

		if isinstance(base_url, RestRequest):
			base_url = base_url.base_url

		parsed_base = urlparse(base_url)
		parsed_full = urlparse(full_url)

		if not full_url.startswith(base_url):
			raise RestRequest.Error("The full URL must start with the base URL.")

		endpoint = parsed_full.path[len(parsed_base.path):].lstrip("/")
		params = {k: v[0] if len(v) == 1 else v for k, v in parse_qs(parsed_full.query).items()}

		return template.copy(base_url=base_url, endpoint=endpoint, params=params)


