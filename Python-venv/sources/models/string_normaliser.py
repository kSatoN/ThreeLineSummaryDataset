# Apache License, Version 2.0の「mojimoji」（by Studio Ousia）を用いています。
from typing import List, Tuple, Pattern, Optional, Union, Match
from itertools import chain
from spacy.lang.ja import Japanese
from spacy.tokens.doc import Doc
from spacy.tokens import Token
from logging import getLogger, Logger
from pprint import pformat
from kanjize import kanji2int
import spacy
import re
import mojimoji
import unicodedata

from .my_tuple import MyTuple


class StringNormaliser:
	"""文字列正規化器。"""
	
	def __init__(self, logger: Logger = None):
		self.__japanese_processor: Japanese = spacy.load("ja_ginza")
		self.__logger: Logger = logger if logger is not None else getLogger("learn")
	
	def normalise(self, string: str, delimiter: str = "。") -> str:
		"""フルコースで文字列を正規化します。\n
		:param string: 正規化前文字列
		:param delimiter: 文区切り文字（例：「。」）
		:return: 正規化後の文字列"""
		unicode_normalised: str = self.unicode_normalise(string)
		crlf2space1: str = self.replace_carriage_return_line_feed_to_space(unicode_normalised)
		# 今回あまり必要なさそうだが，↑により空白2連続が発生する可能性があるため，念のため。
		crlf2space2: str = self.replace_crlf_to_space_with_delimiter(crlf2space1, delimiter)
		sign_replaced: str = self.replace_sign_to_full_width(crlf2space2)
		kan_suji_replaced: str = self.replace_number_to_arabic(sign_replaced)
		return self.replace_full_to_half_width(kan_suji_replaced)
	
	def unicode_normalise(self, string: str) -> str:
		"""Unicode正規化形式Dに正規化します。"""
		return unicodedata.normalize("NFD", string)
	
	def replace_carriage_return_line_feed_to_space(self, before_string: str) -> str:
		"""CRLF，LF，CRを空白文字に置き換えます。そもそもCRって使うことあるのかー？"""
		return before_string.replace("\r\n", "　").replace("\n", "　").replace("\r", "　")
	
	def replace_crlf_to_space_with_delimiter(self, before_string: str, delimiter: str) -> str:
		"""delimiterCRLF or SPACE→除去，[^delimiter]*CRLF→置換，「　」{2, ∞}→「　」{1}　※ delimiter：（例：「。」）"""
		pattern1: Pattern = re.compile(delimiter + "(([ 　]{0,}(\r\n)|(\n)|(\r))|([ 　]{1,}))")
		remove_crlf: str = pattern1.sub(delimiter, before_string)
		replaced_crlf: str = self.replace_carriage_return_line_feed_to_space(remove_crlf)
		pattern2: Pattern = re.compile("[ 　]{2,}")
		return pattern2.sub("　", replaced_crlf)
	
	def replace_sign_to_full_width(self, before_string: str) -> str:
		"""ASCII半角記号は正規表現などいろいろと影響しそうなので全角記号に置き換えます。"""
		# 半角→全角にする記号
		half: str = "\"#%&'()*+" + "<=>?@" + "[\]^`" + "{|}~" + "‐"
		full: str = "＂＃％＆＇（）＊＋" + "＜＝＞？＠" + "［＼］＾｀" + "｛｜｝〜" + "-"
		translate_table = str.maketrans(half, full)
		return before_string.translate(translate_table)
	
	def replace_number_to_arabic(self, before_string: str) -> str:
		"""漢数字を算用数字に置き換えます。"""
		kanji_pattern: Pattern = re.compile("[〇一二三四五六七八九十百千万億兆]{1,}")
		return kanji_pattern.sub(self.__kanji_number_to_arabic_number, before_string)
	
	def __kanji_number_to_arabic_number(self, kanji_match: Match) -> str:
		# 位取りがなく，数字だけが並んでるパターン（例：「二五二」であって「二百五十二」でない）
		divided_pattern: Pattern = re.compile("[〇一二三四五六七八九]{1,}")
		kanji_string: str = kanji_match.group(0)
		divided_match: Match = divided_pattern.fullmatch(kanji_string)
		if divided_match:
			return "".join(MyTuple(kanji_string).map(kanji2int).map(str).tuple)
		return str(kanji2int(kanji_string))
	
	def replace_full_to_half_width(self, before_string: str) -> str:
		"""英数字は半角に揃えます。"""
		translate_table = self.__set_translate_table_latin( )
		translate_latin: str =  before_string.translate(translate_table)
		return mojimoji.han_to_zen(translate_latin, digit = False, ascii = False)
	
	def __set_translate_table_latin(self) -> dict:
		half_character = list( )
		full_character = list( )
		# 数字
		for i in range(10):
			half_character.append(chr(0x0030 + i))
			full_character.append(chr(0xff10 + i))
		# 英大文字
		for i in range(26):
			half_character.append(chr(0x0041 + i))
			full_character.append(chr(0xff21 + i))
		# 英小文字
		for i in range(26):
			half_character.append(chr(0x0061 + i))
			full_character.append(chr(0xff41 + i))
		half: str = "".join(half_character)
		full: str = "".join(full_character)
		return str.maketrans(full, half)
	
	def morphological_analyse(self, string: str) -> Tuple[str, ...]:
		"""形態素解析します。\n
		:param string: 解析文字列
		:return: 形態素に分割したタプル　例：('銀座', 'で', 'ランチ', 'を', 'ご', '一緒', 'し', 'ましょう')"""
		documents: spacy.tokens.doc.Doc = self.__japanese_processor(string)
		# documents.sents：[ [token11, token12, ...], [token21, token22, ...], sentence3, ...]　※ token：形態素
		tokens: MyTuple[Token, ...] = MyTuple(tuple(chain.from_iterable(documents.sents)))
		# 文字列化（表層形の文字列のみにする）
		# tokens.filter(lambda token: token.pos_ != "ADP" and token.pos_ != "AUX" and token.pos_ != "PUNCT" and token.pos_ != "SYM")
		return tokens.map(str).tuple
	
	def morphological_analyse_with_stop_words(self, string: str) -> Tuple[str, ...]:
		"""形態素解析します。\n
		:param string: 解析文字列
		:return: 形態素に分割したタプル　例：('銀座', 'で', 'ランチ', 'を', 'ご', '一緒', 'し', 'ましょう')"""
		documents: spacy.tokens.doc.Doc = self.__japanese_processor(string)
		# documents.sents：[ [token11, token12, ...], [token21, token22, ...], sentence3, ...]　※ token：形態素
		tokens: MyTuple[Token, ...] = MyTuple(tuple(chain.from_iterable(documents.sents)))
		return tokens.filter(lambda token: token.pos_ != "ADP" and token.pos_ != "AUX" and token.pos_ != "PUNCT" and token.pos_ != "SYM" and token.pos_ != "INTJ" and token.pos_ != "SCONJ" and token.pos_ != "DET" and token.pos_ != "PART" and token.pos_ != "X" and "非自立可能" not in token.tag_ and token.lemma_ != "する" and token.lemma_ != "こと" and token.lemma_ != "ある" and token.lemma_ != "いる" and token.lemma_ != "有る" and token.orth_ != "いう" and token.orth_ != "つい" and token.orth_ != "まあ").map(str).tuple
