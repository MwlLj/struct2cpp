# encoding=utf8
import sys
import os
import uuid
sys.path.append("../base")
import re
from string_tools import CStringTools
from file_handle_re import CFileHandle
from parse_gostruct import CGoStructParse
from write_cpp_base import CWriteCppBase


class CStruct2Class(CWriteCppBase):
	def __init__(self, file_path, root="."):
		self.m_file_handler = CFileHandle()
		self.m_file_path = ""
		self.m_content = ""
		self.m_namespace = ""
		self.m_uuid = str(uuid.uuid4())
		self.m_uuid = re.sub(r"-", "", self.m_uuid).upper()
		self.m_struct_list = []
		self.m_class_implement = {}
		self.__compare_file_path(file_path, root)
		CWriteCppBase.__init__(self, self.m_file_path)

	def __compare_file_path(self, file_path, root):
		basename = os.path.basename(file_path)
		filename, fileext = os.path.splitext(basename)
		self.m_file_path = os.path.join(root, filename + ".h")

	def start(self, info_dict):
		self.m_namespace = info_dict.get(CGoStructParse.PACKAGE)
		if self.m_namespace is None:
			raise SystemExit("[ERROR] you should define package")
		struct_list = info_dict.get(CGoStructParse.STRUCT_LIST)
		for struct_info in struct_list:
			# join classes
			struct_name = struct_info.get(CGoStructParse.STRUCT_NAME)
			self.m_struct_list.append(struct_name)
			# join implement
			param_list = struct_info.get(CGoStructParse.PARAM_LIST)
			param_len = len(param_list)
			pls = []
			for param in param_list:
				param_type = self.__type_change(param)
				param_name = self.__name_change(param)
				pls.append((param_type, param_name))
			content = ""
			content += "public:\n"
			if param_len > 0:
				content += "\t" + "explicit {0}()\n\t\t: {1}".format(struct_name, self.write_default_init_param_list(pls)) + " {}\n"
				content += "\t" + "explicit {0}({1})\n\t\t: {2}".format(struct_name, self.write_construction_param_list(pls), self.write_member_init_param_list(pls)) + " {}\n"
			else:
				content += "\t" + "explicit {0}()\n\t".format(struct_name) + "{}\n"
			content += "\t" + "virtual ~{0}()".format(struct_name) + " {}\n"
			content += "\n"
			content += "public:\n"
			for param in param_list:
				param_type = self.__type_change(param)
				param_name = self.__name_change(param)
				content += "\t"
				content += self.write_set_method(param_type, param_name)
				content += "\n"
				content += "\t"
				content += self.write_get_method(param_type, param_name)
				content += "\n"
				content += "\t"
				content += self.write_get_mut_method(param_type, param_name)
				content += "\n"
			content += "\n"
			content += "private:\n"
			for param in param_list:
				param_type = self.__type_change(param)
				param_name = self.__name_change(param)
				content += "\t"
				content += self.write_member_var(param_type, param_name)
				content += "\n"
			self.m_class_implement[(self.m_namespace, struct_name)] = content
		self.write()

	def __type_change(self, param):
		param_type = param.get(CGoStructParse.PARAM_TYPE)
		is_list = param.get(CGoStructParse.PARAM_IS_LIST)
		is_map = param.get(CGoStructParse.PARAM_IS_MAP)
		map_key = param.get(CGoStructParse.PARAM_TYPE_MAP_KEY)
		map_value = param.get(CGoStructParse.PARAM_TYPE_MAP_VALUE)
		if is_list is True:
			t, is_custom_type = self.type_change(param_type)
			param_type = "std::vector<{0}>".format(t)
		if is_map is True:
			t_key, is_custom_type = self.type_change(map_key)
			t_value, is_custom_type = self.type_change(map_value)
			param_type = "std::map<{0}, {1}>".format(t_key, t_value)
		return param_type

	def __name_change(self, param):
		param_name = param.get(CGoStructParse.PARAM_NAME)
		reflex_content = param.get(CGoStructParse.REFLEX_CONTENT)
		if reflex_content is not None:
			param_name = reflex_content
		return param_name

	def is_debug(self):
		return False

	def is_header(self):
		return True

	def define_name(self):
		# #ifndef xxx
		# #define xxx
		return "__{0}_{1}_H__".format(self.m_namespace.upper(), self.m_uuid)

	def include_sys_list(self):
		# #include <xxx>
		return ["string", "vector"]

	def include_other_list(self):
		# #include "xxx"
		return []

	def namespace_list(self):
		# [(namespace1, [class1, class2]), (namespace2, [class1, class2])]
		return [(self.m_namespace, self.m_struct_list)]

	def implement(self, namespace_name, class_name):
		content = self.m_class_implement.get((namespace_name, class_name))
		return content

	def namespace_implement_begin(self, namespace):
		return ""

	def namespace_implement_end(self, namespace):
		return ""

	def type_change(self, param_type):
		is_custom_type = False
		if param_type == "string":
			param_type = "std::string"
		elif param_type == "int8":
			param_type = "char"
		elif param_type == "uint8":
			param_type = "unsigned char"
		elif param_type == "int16":
			param_type = "short"
		elif param_type == "uint16":
			param_type = "unsigned short"
		elif param_type == "int32":
			param_type = "int"
		elif param_type == "uint32":
			param_type = "unsigned"
		elif param_type == "uint":
			param_type = "unsigned"
		elif param_type == "int64":
			param_type = "long long"
		elif param_type == "uint64":
			param_type = "unsigned long long"
		elif param_type == "float32":
			param_type = "float"
		elif param_type == "float64":
			param_type = "double"
		else:
			is_custom_type = True
		return param_type, is_custom_type


if __name__ == "__main__":
	parser = CGoStructParse("./example_struct/test.struct")
	parser.read()
	info_dict = parser.get_info_dict()
	writer = CStruct2Class(parser.get_file_path(), root="example_struct/output")
	writer.start(info_dict)
