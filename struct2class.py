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
from write_base import CWriteBase


class CStruct2Class(CWriteCppBase, CWriteBase):
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
			pls = []
			for param in param_list:
				param_type = param.get(CGoStructParse.PARAM_TYPE)
				param_type = self.cpp_type_change(param_type)
				param_name = param.get(CGoStructParse.PARAM_NAME)
				pls.append((param_type, param_name))
			content = ""
			content += "public:\n"
			content += "\t" + "explicit {0}()\n\t\t: {1}".format(struct_name, self.write_default_init_param_list(pls)) + " {}\n"
			content += "\t" + "explicit {0}({1})\n\t\t: {2}".format(struct_name, self.write_construction_param_list(pls), self.write_member_init_param_list(pls)) + " {}\n"
			content += "\t" + "virtual ~{0}()".format(struct_name) + " {}\n"
			content += "\n"
			content += "public:\n"
			for param in param_list:
				param_type = param.get(CGoStructParse.PARAM_TYPE)
				param_type = self.cpp_type_change(param_type)
				param_name = param.get(CGoStructParse.PARAM_NAME)
				content += "\t"
				content += self.write_set_method(param_type, param_name)
				content += "\n"
				content += "\t"
				content += self.write_get_method(param_type, param_name)
				content += "\n"
			content += "\n"
			content += "private:\n"
			for param in param_list:
				param_type = param.get(CGoStructParse.PARAM_TYPE)
				param_type = self.cpp_type_change(param_type)
				param_name = param.get(CGoStructParse.PARAM_NAME)
				content += "\t"
				content += self.write_member_var(param_type, param_name)
				content += "\n"
			self.m_class_implement[(self.m_namespace, struct_name)] = content
		self.write()

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
		return ["string"]

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


if __name__ == "__main__":
	parser = CGoStructParse("./example_struct/test.struct")
	parser.read()
	info_dict = parser.get_info_dict()
	writer = CStruct2Class(parser.get_file_path(), root="example_struct/output")
	writer.start(info_dict)
