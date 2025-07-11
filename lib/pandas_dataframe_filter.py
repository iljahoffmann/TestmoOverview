from abc import ABCMeta, abstractmethod
from pandas.core.frame import DataFrame



class FilterRegistry:
	_filters = {}

	@classmethod
	def register_filter(cls, filter_cls):
		filter_name = filter_cls.name()
		cls._filters[filter_name] = filter_cls

	@classmethod
	def get_filter(cls, name) -> "FilterBase":
		return cls._filters.get(name)

	@classmethod
	def all_filters(cls) -> dict[str, "FilterBase"]:
		return dict(cls._filters)


class FilterMeta(ABCMeta):
	def __init__(cls, name, bases, namespace):
		super().__init__(name, bases, namespace)
		# Only register subclasses, not FilterBase itself - hide filters without a name
		if name != 'FilterBase' and hasattr(cls, 'name') and getattr(cls, 'name')() is not None:
			FilterRegistry.register_filter(cls)


class FilterBase(metaclass=FilterMeta):
	@classmethod
	@abstractmethod
	def name(cls) -> str:
		"""Return the unique name of the filter."""
		...

	@classmethod
	@abstractmethod
	def description(cls) -> str:
		"""Return a short description of the filters function."""
		...

	@classmethod
	@abstractmethod
	def apply_to(cls, dataframe: DataFrame) -> DataFrame:
		"""Return the unique name of the filter."""
		...

