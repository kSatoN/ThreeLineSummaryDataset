from typing import Tuple, List, Dict, Union, Optional, Iterable, Pattern, Match
from pathlib import Path
from urllib.request import Request, urlopen
from pprint import pformat
from traceback import format_exception
from bs4 import BeautifulSoup, Tag
from datetime import timedelta
from logging import Logger, getLogger
import re
import json
import sys
import gzip
import time

from my_logger import MyLogger
from models.livedoor_news import LivedoorNews


class Crawler:
	"""Livedoorニュースのクローラーです。"""
	
	def __init__(self, logger: Optional[Logger] = None):
		self.__logger: Logger = logger if logger is not None else getLogger("crawl")
		self.__sources_directory_path: str = str(Path(__file__).parent)
		self.__json_directory_path: str = str(Path(self.__sources_directory_path).joinpath("../dataset/crawl"))
		self.__conf_directory_path: str = str(Path(self.__sources_directory_path).joinpath("../conf"))
		# TODO 本当はファイル開けない場合の例外処理も必要（以下すべてのopenにおいて）
		with open(self.__conf_directory_path + "/User-Agent.txt", mode = "r") as user_agent_conf:
			self.__user_agent: str = user_agent_conf.read( ).replace("\r\n", "").replace("\n", "")
		self.__length: int = 0
		self.__count: int = 0
		self.__error_count: int = 0
		self.__delete_count: int = 0
		self.__critical_count: int = 0
		self.__start_time: float = 0.0
		self.__file_name: str = ""
	
	def main(self):
		# TODO 以下3行，例外処理していないため，別の入力でエラーが発生する
		file_name: str = input("どれをクロールする？（debug / develop / test / train）：")
		range_from: int = int(input("開始インデックスは？（0で指定なし）："))
		range_to: int = int(input("終了インデックスは？（0で指定なし）："))
		self.__file_name = file_name
		self.__crawl(file_name, range_from, range_to)
	
	def __crawl(self, file_name: str, range_from: int, range_to: int):
		"""ひとつのJSONファイルのデータについてクロールを実施します。\n
		:param file_name: JSONのファイル名"""
		self.__logger.info(file_name + " の " + str(range_from) + " から " + str(range_to) + " までを取得します。")
		before_data: Tuple[LivedoorNews, ...] = self.__get_data(file_name, range_from, range_to)
		self.__length = len(before_data)
		if self.__length < 1:
			self.__logger.error("ニュースインスタンスを取得できませんでした。")
			return
		self.__logger.info("取得ニュースインスタンス数：" + str(self.__length))
		self.__start_time = time.time( )
		tuple(map(self.__crawl_one, before_data))
		self.__logger.info("【完了】")
		self.__disp_progress( )
	
	def __get_data(self, file_name: str, range_from: int, range_to: int) -> Tuple[LivedoorNews, ...]:
		"""入力された情報を基に，JSONからLivedoorNewsインスタンスを生成します。\n
		:param file_name: JSONの表示名
		:param range_from: JSONの何番目のオブジェクトから取得するか（0で最初から）
		:param range_to: JSONの何番目までのオブジェクトを取得するか（0で最後まで）
		:return: 生成したLivedoorNewsインスタンスの組"""
		with open(self.__json_directory_path + "/" + file_name + ".json", mode = "r") as json_file:
			data_json: List[Dict[str, Union[int, Optional[bool], str]]] = json.load(json_file)
		all_data: Tuple[LivedoorNews, ...] = tuple(map(lambda dic: LivedoorNews(dic.get("year"), dic.get("month"), dic.get("category"), dic.get("id"), dic.get("is_series")), data_json))
		if range_to == 0:
			range_to = len(all_data)
		return tuple(map(lambda tup: tup[1], filter(lambda tup: range_from <= tup[0] and tup[0] < range_to, enumerate(all_data))))
	
	def __crawl_one(self, news: LivedoorNews):
		"""ひとつのLivedoorNewsインスタンスについて，クロールを実施し，タイトル，要約，記事内容を追加します。\n
		:param news: 処理するLivedoorNewsインスタンス
		:return: 入力と同じインスタンス"""
		self.__disp_progress( )
		self.__count += 1
		html: str = self.__id_to_html(news.id)
		if html == "":
			self.__sleep( )
			return
		article: Dict[str, str] = self.__parse_html(html, news.id)
		if article.get("error") is not None:
			self.__sleep( )
			return
		self.__update_json(news, article)
		self.__sleep( )
		return
	
	def __disp_progress(self):
		"""進捗をログ出力します。"""
		now_time: float = time.time( )
		self.__logger.info("\n−−−−−−−−−−−−−−−−−−−−\n進捗：" + str(self.__count) + " / " + str(self.__length) + "（" + str(round(float(self.__count) / float(self.__length) * 100.0, 2)) + " ％），エラー数：" + str(self.__error_count) + "回（" +str(round(float(self.__error_count) / (float(self.__count) + 0.00001) * 100.0, 2)) + " ％），重大エラー数：" + str(self.__critical_count) + "回（" +str(round(float(self.__critical_count) / (float(self.__count) + 0.00001) * 100.0, 2)) + " ％）\n削除済み数：" + str(self.__delete_count) + "件（" +str(round(float(self.__delete_count) / (float(self.__count) + 0.00001) * 100.0, 2)) + " ％）\n経過時間：" + str(timedelta(seconds = (now_time - self.__start_time))) + "，推定残り時間：" + str(timedelta(seconds = (now_time - self.__start_time) * (float(self.__length) / (float(self.__count) + 0.00001)) - (now_time - self.__start_time))))
	
	def __sleep(self):
		"""クロール間隔を空けるため，いったん10秒おやすみします。"""
		self.__logger.debug("いったん おやすみ 🌙 💤")
		time.sleep(10.0)
	
	def __id_to_html(self, id: int) -> str:
		"""idからHTMLを取得します。"""
		url: str = "https://news.livedoor.com/article/detail/" + str(id) + "/"
		self.__logger.debug("ID→HTML：" + url)
		headers: Dict[str, str] = {
			"User-Agent": self.__user_agent,
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
			"Accept-Language": "ja,en;q=0.5",
			"Accept-Encoding": "gzip",
			"Connection": "keep-alive",
			"Cookie": "",
			"Upgrade-Insecure-Requests": "1",
			"Pragma": "no-cache",
			"Cache-Control": "no-cache"
		}
		http_request: Request = Request(url, headers = headers)
		try:
			with urlopen(http_request) as http_response:
				response_headers: Dict[str, str] = http_response.info( )
				comp_type: str = response_headers["Content-Encoding"] if "Content-Encoding" in response_headers else "gzip"
				content_type: str = response_headers["Content-Type"] if "Content-Type" in response_headers else "text/html; charset=utf-8"
				encoding = content_type[content_type.find("charset=") + 8: ]
				response_byte: bytes = http_response.read( )
				if comp_type == "gzip":
					response_byte = gzip.decompress(response_byte)
				return response_byte.decode(encoding = encoding, errors = "ignore")
		except Exception as exception:
			self.__logger.exception(str(id) + " をクロール中にエラーが発生しました。")
			self.__error_count += 1
			return ""
	
	def __parse_html(self, html: str, id: int) -> Dict[str, str]:
		"""HTMLからタイトル，要約，本文を抽出します。\n
		:param html: HTML形式の文字列
		:param id: 記事ID
		:return: { 'title': '(title)', 'summary': '(summary)', 'content': '(content)' }，エラーの場合{ 'error': '(error)' }"""
		self.__logger.debug("HTML解析")
		beautiful_soup: BeautifulSoup = BeautifulSoup(markup = html, features = "html5lib")
		try:
			# 「。」区切りでひとまとまりになっているためmetaタグから要約を取得
			meta_discription: Tag = beautiful_soup.find(name = "meta", attrs = {"name": "description"})
			summary: str = meta_discription.get("content") + "。"
			# 付加情報が付いていないためmetaタグからタイトルを取得
			meta_ob_title: Tag = beautiful_soup.find(name = "meta", attrs = {"property": "ob:title"})
			title: str = meta_ob_title.get("content")
		except Exception as exception:
			self.__logger.exception(str(id) + " を解析中にエラーが発生しました。")
			self.__error_count += 1
			return {"error": "error"}
		try:
			# 本文を取得（サイトの本文前後のタグに間違いがあるため正しく取れる保証はない）
			span_article: Tag = beautiful_soup.find(name = "div", attrs = {"class": "articleBody"}).find(name = "span", attrs = {"itemprop": "articleBody"})
			tuple(map(lambda script: script.decompose( ), span_article.find_all(name = "script")))
			content: str = span_article.get_text(separator = "", strip = True).replace("\r\n", "").replace("\n", "")
		except Exception as exception:
			self.__logger.error("【削除】" + str(id) + " はすでに削除されています。")
			self.__error_count += 1
			self.__delete_count += 1
			return {"error": "error"}
		return self.__check_html(title, summary, content)
	
	def __check_html(self, title: str, summary: str, content: str) -> Dict[str, str]:
		"""HTML解析結果が正しかったか確認します。\n
		:param title: HTMLから取得したタイトル
		:param summary: HTMLから取得した要約
		:param content: HTMLから取得した本文
		return: { 'title': '(title)', 'summary': '(summary)', 'content': '(content)' }，エラーの場合{ 'error': '(error)' }"""
		is_title: bool = 1 < len(title)
		summary_pattern: Pattern = re.compile("[\\W\\w]{1,}?。[\\W\\w]{1,}?。[\\W\\w]{1,}?。")
		summary_match: Match = summary_pattern.fullmatch(summary)
		is_summary: bool = summary_match is not None and 1 < len(summary_match.group(0))
		is_content: bool = 1 < len(content)
		if not (is_title and is_summary and is_content):
			self.__error_count += 1
			self.__logger.error("HTMLの解析結果が正しくないようです。")
			return {"error": "error"}
		return {
			"title": title,
			"summary": summary,
			"content": content
		}
	
	def __update_json(self, news: LivedoorNews, article: Dict[str, str]):
		"""取得した記事情報を元にJSONを更新します"""
		self.__logger.debug("JSON書き込み")
		news.title = article.get("title")
		news.summary = article.get("summary")
		news.content = article.get("content")
		write_data: dict = news.dict_like_json
		try:
			json_string: str = json.dumps(write_data, ensure_ascii = False, allow_nan = False, indent = "\t").replace("\n", "\r\n") + "\r\n"
			with open(self.__json_directory_path + "/" + self.__file_name + "/" + str(news.id) + ".json", mode = "w") as json_write_file:
				json_write_file.write(json_string)
		except Exception as exception:
			self.__error_count += 1
			self.__critical_count += 1
			self.__logger.error("【重大】" + self.__file_name + " JSONファイルに書き込めませんでした。\nID：" + str(id) + "\n処理番号（count）：" + str(self.__count) + "\n更新データ：" + json.dumps(news.dict_like_json, ensure_ascii = False, allow_nan = False, indent = "\t").replace("\n", "\r\n"))
			return


if __name__ == "__main__":
	logger: Logger = MyLogger("crawl").logger
	Crawler(logger).main( )
