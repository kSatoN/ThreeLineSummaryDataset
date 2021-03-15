from typing import Iterable, Tuple, List, Dict, Union, Optional
from pathlib import Path
from multiprocessing.pool import Pool
from logging import Logger, getLogger
import multiprocessing
import csv
import json

from my_logger import MyLogger
from models.livedoor_news import LivedoorNews


class CsvToJson:
	"""CSV→JSON変換器"""
	
	def __init__(self, logger: Optional[Logger] = None):
		self.__logger: Logger = logger if logger is not None else getLogger("CsvToJson")
		self.__sources_directory_path: str = str(Path(__file__).parent)
		self.__csv_directory_path: str = str(Path(self.__sources_directory_path).joinpath("../../data"))
		self.__output_directory_path: str = str(Path(self.__sources_directory_path).joinpath("../dataset/crawl"))
	
	def main(self):
		self.__logger.info("元のCSVのデータをJSONに変換します。")
		converting_files: Tuple[str, str, str, str] = ("debug", "develop", "test", "train")
		with Pool(processes = multiprocessing.cpu_count( ) - 1) as pool:
			results: Iterable[int] = pool.imap(csv_to_json, converting_files)
			counts = tuple(results)
		self.__logger.info("すべてJSONに変換しました。\ndebug：" + str(counts[0]) + " 個\ndevelop：" + str(counts[1]) + " 個\ntest：" + str(counts[2]) + " 個\ntrain：" + str(counts[3]) + " 個")
	
	def csv_to_json(self, file_name: str) -> int:
		self.__logger.debug(file_name + " を変換します。")
		with open(self.__csv_directory_path + "/" + file_name + ".csv", mode = "r") as csv_file:
			reader = csv.reader(csv_file)
			articles: Tuple[dict, ...] = tuple(map(self.csv_row_to_livedoor_news_dict, reader))
		json_string: str = json.dumps(articles, ensure_ascii = False, allow_nan = False, indent = "\t").replace("\n", "\r\n")
		with open(self.__output_directory_path + "/" + file_name + ".json", mode = "w") as json_file:
			json_file.write(json_string + "\r\n")
		self.__logger.debug(file_name + " の変換が終了しました。")
		return len(articles)
	
	def csv_row_to_livedoor_news_dict(self, row: List[str]) -> Dict[str, Union[int, Optional[bool], str]]:
		count: int = len(row)
		if count == 4:
			# 「.」「j」などが何を表しているか不明なため，また少なくともIDではないことから，削除
			temp_id: str = row[3].replace(".", "").replace(".j", "").replace("j", "").replace("s", "")
			return LivedoorNews(int(row[0]) + 2000, int(row[1]), int(row[2]), int(temp_id)).dict_like_json
		return LivedoorNews(int(row[0]) + 2000, int(row[1]), int(row[2]), int(row[3]), row[4] == "1").dict_like_json


def csv_to_json(file_name: str) -> int:
	return CsvToJson( ).csv_to_json(file_name)


if __name__ == "__main__":
	logger: Logger = MyLogger("CsvToJson").logger
	CsvToJson(logger).main( )
