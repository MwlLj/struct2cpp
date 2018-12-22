import sys
import os
import re
sys.path.append("../base/")


class CWriteBase(object):
	def cpp_type_change(self, param_type):
		if param_type == "string":
			param_type = "std::string"
		if param_type == "int8":
			param_type = "char"
		if param_type == "uint8":
			param_type = "unsigned char"
		if param_type == "int16":
			param_type = "short"
		if param_type == "uint16":
			param_type = "unsigned short"
		if param_type == "int32":
			param_type = "int"
		if param_type == "uint32":
			param_type = "unsigned"
		if param_type == "uint":
			param_type = "unsigned"
		if param_type == "int64":
			param_type = "long long"
		if param_type == "uint64":
			param_type = "unsigned long long"
		if param_type == "float32":
			param_type = "float"
		if param_type == "float64":
			param_type = "double"
		return param_type
