# encoding=utf8
import sys
import os
import shutil
sys.path.append("../base")
from file_handle_re import CFileHandle
from cmdline_handle import CCmdlineHandle
from parse_gostruct import CGoStructParse
from struct2class import CStruct2Class


class CCmdHandle(CCmdlineHandle):
	MODE_CREATE = 1
	MODE_UPDATE = 2
	def __init__(self):
		CCmdlineHandle.__init__(self)
		self.m_file_path = None
		self.m_obj = "."
		self.m_cpp_obj = None
		self.m_h_obj = None
		self.m_is_help = False
		self.m_mode = CCmdHandle.MODE_UPDATE

	def get_register_dict(self):
		return {"-f": 1, "-o": 1, "-co": 1, "-ho": 1, "-h": 0, "-create": 0, "-update": 0}

	def single_option(self, option, param_list):
		if option == "-h":
			self.m_is_help = True
			self.__print_help_info()
		elif option == "-f":
			file_path = param_list[0]
			self.m_file_path = file_path
		elif option == "-o":
			self.m_obj = param_list[0]
		elif option == "-co":
			self.m_cpp_obj = param_list[0]
		elif option == "-ho":
			self.m_h_obj = param_list[0]
		elif option == "-create":
			self.m_mode = CCmdHandle.MODE_CREATE
		elif option == "-update":
			self.m_mode = CCmdHandle.MODE_UPDATE

	def param_error(self, option):
		if option == "-f":
			print("please input filepath")
		elif option == "-o":
			print("please input objpath")
		elif option == "-co":
			print("please input objpath")
		elif option == "-ho":
			print("please input objpath")

	def __create_dirs(self, path):
		if os.path.exists(path) is False:
			os.makedirs(path)

	def parse_end(self):
		if self.m_is_help is True:
			return
		if self.m_file_path is None:
			print("please input filepath")
			return
		isExist = os.path.exists(self.m_file_path)
		if isExist is False:
			print("file is not exist")
			return
		# 判断输出目录是否存在
		obj_flag = False
		cpp_obj_flag = False
		h_obj_flag = False
		self.__create_dirs(self.m_obj)
		h_obj = self.m_obj
		if self.m_h_obj is not None:
			h_obj = self.m_h_obj
		self.__create_dirs(h_obj)
		cpp_obj = self.m_obj
		if self.m_cpp_obj is not None:
			cpp_obj = self.m_cpp_obj
		self.__create_dirs(cpp_obj)
		parser = CGoStructParse(self.m_file_path)
		parser.read()
		info_dict = parser.get_info_dict()
		# 写参数类
		writer = CStruct2Class(parser.get_file_path(), root=h_obj)
		writer.start(info_dict)
		"""
		if self.m_mode == CCmdHandle.MODE_CREATE:
			writer = CWriteSqliteImpH(parser.get_file_path(), root=h_obj)
			writer.write(info_dict)
			writer = CWriteSqliteImpCpp(parser.get_file_path(), root=cpp_obj)
			writer.write(info_dict)
		"""

	def __print_help_info(self):
		info = "\n\toptions:\n"
		info += "\t\t-h: help\n"
		info += "\t\t-f: *.sql file path\n"
		info += "\t"*2 + "-o: output file path\n"
		info += "\t"*2 + "-ho: output .h file path\n"
		info += "\t"*2 + "-co: output .cpp file path\n"
		info += "\t"*2 + "-create: create files\n"
		info += "\t"*2 + "-update: update files\n"
		info += "\n" + "\t"*1 + "for example:\n"
		info += "\t"*2 + "python -create ./main.py -f ./file/xxx.sql -ho ./project/handler/include -co ./project/handler/source\n"
		info += "\t"*2 + "python -update ./main.py -f ./file/xxx.sql -ho ./project/handler/include -co ./project/handler/source\n"
		info += "\n"
		print(info)


if __name__ == "__main__":
	handle = CCmdHandle()
	handle.parse()
