from typing import Optional
from logging import getLogger, StreamHandler, Formatter, FileHandler, DEBUG, Logger
from pathlib import Path
from datetime import date
import sys


class MyLogger( ):
	"""ロガーです。"""
	
	def __init__(self, name: Optional[str] = None):
		self.__sources_directory_path: str = str(Path(__file__).parent)
		self.__log_directory_path: str = str(Path(self.__sources_directory_path).joinpath("../log"))
		self.__logger: Logger = self.__setup_logger(name) if name is not None else self.__setup_logger("default")
	
	@property
	def logger(self) -> Logger:
		return self.__logger
	
	def __setup_logger(self, name: str = __name__) -> Logger:
		logger: Logger = getLogger(name)
		logger.setLevel(DEBUG)
		stream_handler: StreamHandler = StreamHandler(sys.stdout)
		stream_handler.setLevel(DEBUG)
		# formatter: Formatter = Formatter('[%(asctime)s: %(levelname)s: (%(name)s)] %(message)s')
		formatter: Formatter = Formatter("\n[\033[95m%(asctime)s.%(msecs)03d\033[00m:\033[96m%(module)s\033[00m:\033[93m%(levelname)s\033[00m] %(message)s", datefmt = "%Y/%m/%d-%H:%M:%S")
		stream_handler.setFormatter(formatter)
		logger.addHandler(stream_handler)
		file_handler: FileHandler = FileHandler(self.__log_directory_path + "/" + str(date.today( )) + ".html")
		file_handler.setLevel(DEBUG)
		file_formatter: Formatter = HTMLFormatter(fmt = '<p>[<span style="color: #ff3030;">%(asctime)s.%(msecs)03d</span>:<span style="color: #0080ff;">%(module)s</span>:<span style="color: #00a000;">%(levelname)s</span>] %(message)s</p>\r\n', datefmt = "%Y/%m/%d-%H:%M:%S")
		file_handler.setFormatter(file_formatter)
		logger.addHandler(file_handler)
		return logger


class HTMLFormatter(Formatter):
	def __init__(self, fmt: str, datefmt: str):
		super( ).__init__(fmt, datefmt)
	
	def format(self, record) -> str:
		record.message = record.getMessage( ).replace("<", "&#60").replace(">", "&#62").replace("\r\n", "<br />").replace("\n", "<br />").replace("\t", "　　")
		if self.usesTime( ):
			record.asctime = self.formatTime(record, self.datefmt)
		s = self.formatMessage(record)
		if record.exc_info:
			if not record.exc_text:
				record.exc_text = self.formatException(record.exc_info)
		if record.exc_text:
			if s[-1:] != "\n":
				s = s + "\n"
			s = s + record.exc_text
		if record.stack_info:
			if s[-1:] != "\n":
				s = s + "\n"
			s = s + self.formatStack(record.stack_info)
		return s
