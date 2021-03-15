from typing import Dict, Union, Optional


class LivedoorNews:
	"""Livedoorニュースの記事です。"""
	
	def __init__(self, year: int, month: int, category: int, id: int, is_series: Optional[bool] = None, title: str = "", summary: str = "", content: str = ""):
		"""記事インスタンスを生成します。\n
		:param year: 公開年
		:param month: 公開月
		:param category: 記事カテゴリー（フォークのため詳細は不明）
		:param id: 記事ID（URLの最後の部分）
		:param is_series: 記事タイプが直列か（直列→True，並列→False）
		:param title: 記事タイトル
		:param summary: 「ざっくり言うと」（3行要約），行は「。」区切り
		:param content: 記事の中身"""
		self.__year: int = year
		self.__month: int = month
		self.__category: int = category
		self.__id: int = id
		self.__is_series: bool = is_series
		self.__title: str = title
		self.__summary: str = summary
		self.__content: str = content
	
	@property
	def year(self) -> int:
		"""公開年"""
		return self.__year
	
	@property
	def month(self) -> int:
		"""公開月"""
		return self.__month
	
	@property
	def category(self) -> int:
		"""記事カテゴリー"""
		return self.__category
	
	@property
	def id(self) -> int:
		"""記事ID（URLの最後の部分）"""
		return self.__id
	
	@property
	def is_series(self) -> bool:
		"""記事タイプが直列か（直列→True，並列→False）"""
		return self.__is_series
	
	@property
	def title(self) -> str:
		"""記事タイトル"""
		return self.__title
	
	@title.setter
	def title(self, value: str):
		"""記事タイトル"""
		self.__title = value
	
	@property
	def summary(self) -> str:
		"""「ざっくり言うと」（3行要約），行は「。」区切り"""
		return self.__summary
	
	@summary.setter
	def summary(self, value: str):
		"""「ざっくり言うと」（3行要約），行は「。」区切り"""
		self.__summary = value
	
	@property
	def content(self) -> str:
		"""記事の中身"""
		return self.__content
	
	@content.setter
	def content(self, value: str):
		"""記事の中身"""
		self.__content = value
	
	@property
	def dict_like_json(self) -> Dict[str, Union[int, Optional[bool], str]]:
		"""インスタンスの状態をJSON風の辞書で表現します"""
		return {
			"year": self.__year,
			"month": self.__month,
			"category": self.__category,
			"id": self.__id,
			"is_series": self.__is_series,
			"title": self.__title,
			"summary": self.__summary,
			"content": self.__content
			}
