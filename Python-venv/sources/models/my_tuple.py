from functools import reduce
from typing import Callable, Iterable, Any, Optional
from logging import Logger
from multiprocessing import Pool
from multiprocessing.pool import IMapIterator
import multiprocessing


class MyTuple(tuple):
	"""map，reduce，filterをメソッドとして実装した，独自tupleです。"""
	
	def __init__(self, iterator: Iterable):
		# super(MyTuple, self).__init__(iterator)
		self.__iterator: Iterable = iterator
	
	@property
	def tuple(self) -> tuple:
		"""処理結果を標準tupleで返します。"""
		return tuple(self.__iterator)
	
	@property
	def list(self) -> list:
		"""処理結果を標準listで返します。"""
		return list(self.__iterator)
	
	def to_tuple(self):
		self.__iterator = tuple(self.__iterator)
		return self
	
	def map(self, function: Callable):
		"""引数の写像を計算します。"""
		self.__iterator = map(function, self.__iterator)
		return self
	
	def imap(self, function: Callable, num_of_process: int = multiprocessing.cpu_count( ) - 1):
		"""引数の写像を並列（別プロセス）で計算します。"""
		with Pool(processes = num_of_process) as pool:
			result: IMapIterator = pool.imap(function, self.__iterator)
			self.__iterator = tuple(result)
		return self
	
	def reduce(self, function: Callable):
		"""畳み込み演算します。"""
		self.__iterator = reduce(function, self.__iterator)
		return self
	
	def filter(self, function: Callable[[Any], bool]):
		"""抽出をします。"""
		self.__iterator = filter(function, self.__iterator)
		return self
	
	def print_count(self, message: str = "", logger: Optional[Logger] = None):
		self.__iterator = tuple(self.__iterator)
		logger.info(message + str(len(self.__iterator))) if logger is not None else print(message + str(len(self.__iterator)))
		return self
