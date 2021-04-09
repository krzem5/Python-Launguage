import colorama
import importlib
import json
import ntpath
import os
import pickle
import shutil
import sys
import time



BUILTIN_MODULE_FOLDER_PATH="./modules/"
TEMP_FOLDER_PATH="./tmp/"



sys.path.append(ntpath.join(ntpath.split(__file__)[0],TEMP_FOLDER_PATH))



colorama.init()



def write(t):
	print("\033[22;37m"+t,end="")
def write_warn(w):
	print("\033[2;33m"+w,end="")
def write_error(e):
	print("\033[2;31m"+e,end="")



class Error:
	def __init__(self,s,e,_i=False):
		self.ERROR=True
		self.stack=s
		self.e=e
		self.msg=(e if _i==False else "")
	def print(self):
		s="Error:\n"
		rp=None
		for p in self.stack:
			if (ntpath.isfile(p[0])):
				rp=p[0]
				s+=f"  File {p[0]}, line {p[1]} in <main>:\n{p[2]}\n"
			else:
				s+=f"  File {rp}, line {p[1]} in '{p[0]}':\n{p[2]}\n"
		s+="\n"+self.msg+"\n"
		return s



class SyntaxError(Error):
	def __init__(self,s,e,_i=False):
		super().__init__(s,e,True)
		self.msg+="Syntax Error: "+(e if _i==False else "")
class TypeError(Error):
	def __init__(self,s,e,_i=False):
		super().__init__(s,e,True)
		self.msg+="Type Error: "+(e if _i==False else "")
class OverrideError(Error):
	def __init__(self,s,e,_i=False):
		super().__init__(s,e,True)
		self.msg+="Override Error: "+(e if _i==False else "")
class ImportError(Error):
	def __init__(self,s,e,_i=False):
		super().__init__(s,e,True)
		self.msg+="Import Error: "+(e if _i==False else "")



class UnexpectedCharacterError(SyntaxError):
	def __init__(self,s,e,_i=False):
		super().__init__(s,e,True)
		self.msg+="Unexpected Character Error: "+(e if _i==False else "")
class BracketError(SyntaxError):
	def __init__(self,s,e,_i=False):
		super().__init__(s,e,True)
		self.msg+="Bracket Error: "+(e if _i==False else "")
class ArgumentError(SyntaxError):
	def __init__(self,s,e,_i=False):
		super().__init__(s,e,True)
		self.msg+="Argument Error: "+(e if _i==False else "")
class UnsupportedOperatorError(SyntaxError):
	def __init__(self,s,e,_i=False):
		super().__init__(s,e,True)
		self.msg+="Unsupported Operator Error: "+(e if _i==False else "")
class ReassigmentError(OverrideError):
	def __init__(self,s,e,_i=False):
		super().__init__(s,e,True)
		self.msg+="Reassigment Error: "+(e if _i==False else "")



class Class:
	def __init__(self,name,fl):
		self.name=name
		self.fl={}
		for k in fl:
			self.fl[k.name]=k
			k.ac+=[self]
	def __str__(self):
		return self.__repr__()
	def __repr__(self):
		return f"Class(name={self.name}, functions=[{self.fl.values()}])"



class Function:
	def __init__(self,name,r_type,params,code,af,av,ac,nt=False):
		self.name=name
		self.r_type=r_type
		self.params=params
		self.code=code
		self.af=af
		self.av=av
		self.ac=ac
		self.import_=None
		self.native=nt
	def __str__(self):
		return self.__repr__()
	def __repr__(self):
		return f"Function(name={self.name}, return_type={self.r_type}, parameters={self.params}, is_native={self.native})"



	def _e(self,params):
		rv=self.import_(params)
		return Variable("",self.r_type,rv)



	def get_vl(self,params=None):
		l=[]
		for i in self.av:
			s=True
			for k in self.params:
				if (i.name==k.name):
					s=False
					break
			if (s==True):
				l.append(i)
		if (params is None):
			if (self.params is not None):
				for p in self.params:
					l.append(p)
		else:
			i=0
			for p in params:
				l.append(Variable(self.params[i].name,self.params[i].type,p.value))
				i+=1
		return l



class Variable:
	def __init__(self,name,type_,value,constant=False):
		self.name=name
		self.type=type_
		self.param=(value=="param")
		if (value=="param"):value=None
		self.value=value
		self.constant=constant
	def __str__(self):
		return self.__repr__()
	def __repr__(self):
		return f"Variable(name={self.name}, type={self.type}, value={self.value}, is_parameter={self.param}, is_constant={self.constant})"



class _Print(Function):
	def __init__(self):
		super().__init__("print","void",None,"",[],[],[],nr=True)



	def exec(self,params):
		s=""
		for p in params:
			if (p.type!="bool"):
				s+=str(p.value)+" "
			else:
				s+=("true" if p.value==True else "false")+" "
		s=s[:-1]
		write(s)
		return Variable("","void","null")



class _Println(Function):
	def __init__(self):
		super().__init__("println","void",None,"",[],[],[],nr=True)



	def exec(self,params):
		s=""
		for p in params:
			if (p.type!="bool"):
				s+=str(p.value)+" "
			else:
				s+=("true" if p.value==True else "false")+" "
		s=s[:-1]
		write(s+"\n")
		return Variable("","void","null")



class _Warn(Function):
	def __init__(self):
		super().__init__("warn","void",None,"",[],[],[],nr=True)



	def exec(self,params):
		s=""
		for p in params:
			if (p.type!="bool"):
				s+=str(p.value)+" "
			else:
				s+=("true" if p.value==True else "false")+" "
		s=s[:-1]
		write_warn(s+"\n")
		return Variable("","void","null")



class _Error(Function):
	def __init__(self):
		super().__init__("error","void",None,"",[],[],[],nr=True)



	def exec(self,params):
		s=""
		for p in params:
			if (p.type!="bool"):
				s+=str(p.value)+" "
			else:
				s+=("true" if p.value==True else "false")+" "
		s=s[:-1]
		write_error(s+"\n")
		return Variable("","void","null")



class _Clear(Function):
	def __init__(self):
		super().__init__("clear","void",None,"",[],[],[],nr=True)



	def exec(self,params):
		os.system("CLS")
		return Variable("","void","null")



class _Int(Function):
	def __init__(self):
		super().__init__("int","int",[Variable("",None,"param")],"",[],[],[],nr=True)



	def exec(self,params):
		r=0
		if (params[0].type=="int"):
			r=params[0].value
		if (params[0].type=="float"):
			r=int(str(params[0].value).split(".")[0])
		if (params[0].type=="bool"):
			r=0
			if (params[0].value==True):
				r=1
		if (params[0].type=="string"):
			r=""
			for c in params[0].value:
				if (c in "0123456789"):
					r+=c
			if (r==""):
				r=0
			else:
				r=int(r)
		return Variable("","int",r)



class _Float(Function):
	def __init__(self):
		super().__init__("float","float",[Variable("",None,"param")],"",[],[],[],nr=True)



	def exec(self,params):
		r=0
		if (params[0].type=="int"):
			r=float(params[0].value)
		if (params[0].type=="float"):
			r=params[0].value
		if (params[0].type=="bool"):
			r=0.0
			if (params[0].value==True):
				r=1.0
		if (params[0].type=="string"):
			r=""
			sp=False
			for c in params[0].value:
				if (c in "0123456789"):
					r+=c
				if (c=="."):
					if (sp==True):
						break
					sp=True
					r+=c
			if (r==""):
				r=0
			else:
				r=float(r)
		return Variable("","float",r)



class _Str(Function):
	def __init__(self):
		super().__init__("str","string",[Variable("",None,"param")],"",[],[],[],nr=True)



	def exec(self,params):
		r=0
		if (params[0].type=="int"):
			r=str(params[0].value)
		if (params[0].type=="float"):
			r=str(params[0].value)
		if (params[0].type=="bool"):
			r="false"
			if (params[0].value==True):
				r="true"
		if (params[0].type=="string"):
			r=params[0].value
		return Variable("","string",r)



class _Bool(Function):
	def __init__(self):
		super().__init__("bool","bool",[Variable("",None,"param")],"",[],[],[],nr=True)



	def exec(self,params):
		r=0
		if (params[0].type=="int"):
			r=False
			if (params[0].value>0):
				r=True
		if (params[0].type=="float"):
			r=False
			if (params[0].value>0):
				r=True
		if (params[0].type=="bool"):
			r=params[0].value
		if (params[0].type=="string"):
			r=(len(params[0].value))
		return Variable("","bool",r)



BUILTIN_FUNCTION_LIST=[_Print(),_Println(),_Warn(),_Error(),_Clear(),_Int(),_Float(),_Str(),_Bool()]



class Compiler:
	C_VERSION="1.0.1"
	RE_VERSION="1.0.0"

	LT_NONE=0
	LT_EMPTY=1
	LT_COMMENT=2
	LT_IMPORT=3
	LT_CLASS_CALL=4
	LT_FUNC_CALL=5
	LT_FUNC_DEF=6
	LT_VAR_DEF=7
	LT_VAR_ASSIGN=8
	LT_IF_STATEMENT=9
	LT_FOR_LOOP=10
	LT_WHILE_LOOP=11

	M_NONE=0
	M_STRING=1

	NORMAL_OPEN_BRACKET="("
	SQUARE_OPEN_BRACKET="["
	CURLY_OPEN_BRACKET="{"
	NORMAL_CLOSE_BRACKET=")"
	SQUARE_CLOSE_BRACKET="]"
	CURLY_CLOSE_BRACKET="}"

	LINE_BREAK_CHAR="\n"
	LINE_BREAK_ESCAPE_CHAR="\r"
	LINE_BREAK_CHARS="\n\r"
	LINE_TERMINATOR_CHAR=";"
	TAB_CHAR="\t"
	SPACE_CHAR=" "
	QUOTE_CHAR="\""
	QUOTE_ESCAPE_CHAR="\\"
	COMMENT_STRING="//"
	UNICODE_ESCAPE_STRING="\\u"
	UNICODE_ESCAPE_LENGTH=4

	FUNC_DEF_STRING="func "
	ALLOWED_FUNC_NAME_START_CHARS="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
	ALLOWED_FUNC_NAME_CHARS="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
	FUNC_PARAMS_START_CHAR="("
	FUNC_PARAMS_END_CHAR=")"
	FUNC_PARAMS_SPILT_CHAR=","
	FUNC_DEF_START_CHAR="{"
	FUNC_DEF_END_CHAR="}"

	VAR_DEF_STRING="var "
	CONST_DEF_STRING="const "
	VAR_DEF_SPLIT_CHAR=","
	VAR_DEF_ASSIGN_CHAR="="
	ALLOWED_VAR_NAME_START_CHARS="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
	ALLOWED_VAR_NAME_CHARS="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"

	ALLOWED_VAR_TYPE_CHARS="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
	ALLOWED_VAR_TYPES="int,string,float,bool".split(",")
	ALLOWED_RETURN_VAR_TYPES="int,string,float,bool,void".split(",")
	VAR_TYPE_START_CHAR="<"
	VAR_TYPE_END_CHAR=">"

	VAR_TYPE_BOOL_TRUE="true"
	VAR_TYPE_BOOL_FALSE="false"

	ALLOWED_TYPE_INT_START_CHARS="0123456789"
	ALLOWED_TYPE_INT_CHARS="0123456789_"

	ALLOWED_TYPE_FLOAT_START_CHARS="0123456789"
	ALLOWED_TYPE_FLOAT_CHARS="0123456789_"
	TYPE_FLOAT_SPLIT_CHAR="."

	OPERATORS="+-*/%^"
	OP_ADD="+"
	OP_SUB="-"
	OP_MULT="*"
	OP_DIV="/"
	OP_MOD="%"
	OP_POW="^"
	OP_OPEN_BRACKET="("
	OP_CLOSE_BRACKET=")"
	MAX_OP_LVL=3
	OP_LVL_3="^"
	OP_LVL_2="*/"
	OP_LVL_1="+-"

	IF_STATEMENT_STRING="if"
	IF_COND_START_CHAR="("
	IF_COND_END_CHAR=")"
	IF_DEF_START_CHAR="{"
	IF_DEF_END_CHAR="}"

	ELSE_STATEMENT_STRING="else"

	COND_SPLIT_CHARS="&&,||"
	COND_AND_CHAR="&&"
	COND_OR_CHAR="||"
	COND_NOT_CHAR="!"
	COND_EQ_CHAR="=="
	COND_NOT_EQ_CHAR="!="
	COND_LESS_CHAR="<"
	COND_NOT_MORE_CHAR="<="
	COND_MORE_CHAR=">"
	COND_NOT_LESS_CHAR=">="
	COND_OPEN_BRACKETS="("
	COND_CLOSE_BRACKETS=")"

	FOR_LOOP_STRING="for"
	FOR_COND_START_CHAR="("
	FOR_COND_END_CHAR=")"
	FOR_COND_DELIMETER=";"
	FOR_INCREMENT_DELIMETER=","
	FOR_DEF_START_CHAR="{"
	FOR_DEF_END_CHAR="}"

	WHILE_LOOP_STRING="while"
	WHILE_COND_START_CHAR="("
	WHILE_COND_END_CHAR=")"
	WHILE_DEF_START_CHAR="{"
	WHILE_DEF_END_CHAR="}"

	IMPORT_STRING="import "
	IMPORT_MODULE_PYTHON_FORMAT=".py.json"
	IMPORT_MODULE_PYTHON_EXT=".py"
	IMPORT_MODULE_CPL_EXT=".cpl"
	IMPORT_MODULE_PYTHON=0
	IMPORT_MODULE_CPL=1

	CLASS_ATTR_SPLIT_CHAR="."
	ALLOWED_CLASS_NAME_START_CHARS="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
	ALLOWED_CLASS_NAME_CHARS="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"


	@staticmethod
	def compile(seq,VL=[],_FL=[],CL=[],S=[],E=True,D=False,C=True):
		def check_start(seq,i):
			while (seq[i] not in Compiler.LINE_BREAK_CHARS):
				if (seq[i]!=Compiler.SPACE_CHAR and seq[i]!=Compiler.TAB_CHAR):
					return False
				i-=1
			return True
		FL=_FL[:]
		ST=0
		if (D==True):
			print("DEBUG \u2012 Compiling "+S[0]+"...")
			ST=time.time()
		if (C==True):
			seq=Compiler.LINE_BREAK_CHAR+seq+Compiler.LINE_BREAK_CHAR
			M=0
			i=0
			while (i<len(seq)):
				if (seq[i]==Compiler.QUOTE_CHAR and ((i==0) or (i>0 and seq[i-1]!=Compiler.QUOTE_ESCAPE_CHAR))):
					if (M==0):
						M=1
					else:
						M=0
				if (check_start(seq,i-1) and seq[i:].startswith(Compiler.FOR_LOOP_STRING)):
					i+=len(Compiler.FOR_LOOP_STRING)
					b=None
					while (b!=0):
						if (seq[i]==Compiler.FOR_COND_START_CHAR):
							if (b is None):b=0
							b+=1
						if (seq[i]==Compiler.FOR_COND_END_CHAR):
							if (b is None):b=0
							b-=1
						i+=1
					continue
				if (i>0 and M==0 and seq[i-1]==Compiler.LINE_TERMINATOR_CHAR and seq[i]!=Compiler.LINE_BREAK_CHAR):
					seq=seq[:i]+Compiler.LINE_BREAK_ESCAPE_CHAR+seq[i:]
				i+=1
		i=1
		li=0
		LT=Compiler.LT_NONE
		M=Compiler.M_NONE
		BR=[]
		fnl=[]
		C=[]
		for f in FL:
			fnl.append(f.name)
		for k in BUILTIN_FUNCTION_LIST:
			if (k.name not in fnl):
				FL.append(k)
		while (True):
			if (i>=len(seq)):break
			# Line not started yet...
			if (check_start(seq,i+0) and seq[i] not in Compiler.LINE_BREAK_CHARS):
				i+=1
				continue
			# Empty line
			if (check_start(seq,i-1) and seq[i] in Compiler.LINE_BREAK_CHARS):
				LT=Compiler.LT_EMPTY
			# Comment
			if (LT==Compiler.LT_NONE and check_start(seq,i-1) and seq[i:].startswith(Compiler.COMMENT_STRING)):
				LT=Compiler.LT_COMMENT
				while (seq[i]!=Compiler.LINE_BREAK_CHAR):
					i+=1
				if (D==True):
					print("DEBUG \u2012 Comment")
			# String
			if (LT==Compiler.LT_NONE and seq[i]==Compiler.QUOTE_CHAR and seq[i-1]!=Compiler.QUOTE_ESCAPE_CHAR):
				if (M==Compiler.M_NONE):
					M=Compiler.M_STRING
				else:
					M=Compiler.M_NONE
			# Import
			if (LT==Compiler.LT_NONE and check_start(seq,i-1) and seq[i:].startswith(Compiler.IMPORT_STRING)):
				LT=Compiler.LT_IMPORT
				i+=len(Compiler.IMPORT_STRING)
				if (ntpath.isfile(S[-1])==False):
					return ImportError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],"Can only import at <main> level")
				nm=""
				while (seq[i]!=Compiler.LINE_TERMINATOR_CHAR and seq[i] not in Compiler.LINE_BREAK_CHARS):
					nm+=seq[i]
					i+=1
				p=ntpath.join(ntpath.split(__file__)[0],BUILTIN_MODULE_FOLDER_PATH,nm)
				mt=None
				if (ntpath.isfile(p+Compiler.IMPORT_MODULE_PYTHON_FORMAT) and ntpath.isfile(p+Compiler.IMPORT_MODULE_PYTHON_EXT)):
					mt=Compiler.IMPORT_MODULE_PYTHON
				elif (ntpath.isfile(p+Compiler.IMPORT_MODULE_CPL_EXT)):
					mt=Compiler.IMPORT_MODULE_CPL
				else:
					p=ntpath.join(os.getcwd(),nm)
					if (ntpath.isfile(p+Compiler.IMPORT_MODULE_PYTHON_FORMAT) and ntpath.isfile(p+Compiler.IMPORT_MODULE_PYTHON_EXT)):
						mt=Compiler.IMPORT_MODULE_PYTHON
					elif (ntpath.isfile(p+Compiler.IMPORT_MODULE_CPL_EXT)):
						mt=Compiler.IMPORT_MODULE_CPL
					else:
						return ImportError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Module '{nm}' not found :(")
				if (mt==Compiler.IMPORT_MODULE_PYTHON):
					data=None
					with open(p+Compiler.IMPORT_MODULE_PYTHON_FORMAT) as f:
						data=json.loads(f.read())
					tmp=shutil.copy(p+Compiler.IMPORT_MODULE_PYTHON_EXT,ntpath.join(ntpath.split(__file__)[0],TEMP_FOLDER_PATH)+"_"+nm+Compiler.IMPORT_MODULE_PYTHON_EXT)
					m=importlib.import_module("_"+nm)
					fl=[]
					for f in data["functions"]:
						pl=[]
						if (f["params"] is None):
							pl=None
						else:
							for k in f["params"]:
								pl+=[Variable("",k,"param")]
						nf=Function(f["name"],f["return_type"],pl,"",[],[],[])
						setattr(nf,"import_",getattr(m,f["func_name"]))
						setattr(nf,"exec",getattr(nf,"_e"))
						fl.append(nf)
					os.remove(tmp)
					CL.append(Class(nm,fl))
					C+=[{"t":"imp","o":"p","v":p+Compiler.IMPORT_MODULE_PYTHON_EXT,"d":p[len(ntpath.split(__file__)[0]):]+Compiler.IMPORT_MODULE_PYTHON_FORMAT,"n":nm}]
				else:
					p+=Compiler.IMPORT_MODULE_CPL_EXT
					data=""
					with open(p,"r") as f:
						data=f.read()
					r=Compiler.compile(data,S=S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")],p],E=False)
					if (hasattr(r,"ERROR") and r.ERROR==True):
						return r
					fl=[]
					for k in r:
						if (k["t"]=="f_def"):
							pl=[]
							for pr in k["p"]:
								pl+=[Variable("",pr["t"],"param")]
							fl+=[Function(k["n"],k["r"],pl,"",[],[],[])]
					CL.append(Class(nm,fl))
					C+=[{"t":"imp","o":"c","v":p,"n":nm}]
			# If / Else statement
			if (LT==Compiler.LT_NONE and check_start(seq,i-1) and seq[i:].startswith(Compiler.IF_STATEMENT_STRING)):
				i+=len(Compiler.IF_STATEMENT_STRING)
				si=i-len(Compiler.IF_STATEMENT_STRING)
				sli=li+0
				while (seq[i]==Compiler.SPACE_CHAR or seq[i]==Compiler.TAB_CHAR):
					i+=1
				if (seq[i]!=Compiler.IF_COND_START_CHAR):
					i=si
				else:
					i+=1
					b=1
					c=""
					while (b!=0):
						c+=seq[i]
						if (seq[i]==Compiler.FUNC_PARAMS_START_CHAR):b+=1
						if (seq[i]==Compiler.FUNC_PARAMS_END_CHAR):b-=1
						if (b==0):
							c=c[:-1]
						i+=1
						if (b!=0 and i>=len(seq) or seq[i] in Compiler.LINE_BREAK_CHARS):
							c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
							return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Expected '{Compiler.IF_COND_END_CHAR}', found '{c}'")
					while (seq[i]==Compiler.SPACE_CHAR or seq[i]==Compiler.TAB_CHAR):
						i+=1
					if (seq[i]!=Compiler.IF_DEF_START_CHAR):
						c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
						return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Expected '{Compiler.IF_DEF_START_CHAR}', found '{c}'")
					i+=1
					code=""
					b=1
					while (b!=0):
						code+=seq[i]
						if (seq[i]==Compiler.IF_DEF_START_CHAR):b+=1
						if (seq[i]==Compiler.IF_DEF_END_CHAR):b-=1
						if (b==0):
							code=code[:-1]
						i+=1
						if (seq[i]==Compiler.LINE_BREAK_CHAR):
							li+=1
						if (b!=0 and i>=len(seq)):
							c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
							return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Expected '{Compiler.IF_DEF_END_CHAR}', found '{c}'")
					LT=Compiler.LT_IF_STATEMENT
					if (D==True):
						print("DEBUG \u2012 If cond")
					c=Compiler.compile_condition(c,VL=VL,FL=FL,CL=CL,S=S[:-1]+[[S[-1],sli+1,seq.split(Compiler.LINE_BREAK_CHAR)[sli+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]])
					if (hasattr(c,"ERROR") and c.ERROR==True):
						return c
					code=Compiler.compile(code,VL=VL[:],FL=FL[:],CL=CL[:],S=S,E=False)
					if (hasattr(code,"ERROR") and code.ERROR==True):
						for i in range(0,len(code.stack)):
							code.stack[i][1]+=sli+1
							if (ntpath.isfile(code.stack[i][0])==True):
								break
						return code
					si=i+0
					sli=li+0
					while (seq[i]==Compiler.SPACE_CHAR or seq[i]==Compiler.TAB_CHAR or seq[i] in Compiler.LINE_BREAK_CHARS):
						if (seq[i]==Compiler.LINE_BREAK_CHAR):
							li+=1
						i+=1
						if (i>=len(seq)):
							break
					ec=None
					if (i<len(seq) and seq[i:].startswith(Compiler.ELSE_STATEMENT_STRING)):
						i+=len(Compiler.ELSE_STATEMENT_STRING)
						while (seq[i]==Compiler.SPACE_CHAR or seq[i]==Compiler.TAB_CHAR or seq[i] in Compiler.LINE_BREAK_CHARS):
							i+=1
						if (seq[i]!=Compiler.IF_DEF_START_CHAR):
							i=si
						else:
							i+=1
							ec=""
							b=1
							sli=li+0
							while (b!=0):
								ec+=seq[i]
								if (seq[i]==Compiler.IF_DEF_START_CHAR):b+=1
								if (seq[i]==Compiler.IF_DEF_END_CHAR):b-=1
								if (b==0):
									ec=ec[:-1]
								i+=1
								if (seq[i]==Compiler.LINE_BREAK_CHAR):
									li+=1
								if (b!=0 and i>=len(seq)):
									c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
									return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Expected '{Compiler.IF_DEF_END_CHAR}', found '{c}'")
							ec=Compiler.compile(ec,VL=VL[:],FL=FL[:],CL=CL,S=S,E=False)
							if (hasattr(ec,"ERROR") and ec.ERROR==True):
								for i in range(0,len(ec.stack)):
									ec.stack[i][1]+=sli+1
									if (ntpath.isfile(ec.stack[i][0])==True):
										break
								return ec
					else:
						i=si
						li=sli
					C+=[{"t":"if_c","c":c,"v":code,"e":ec}]
			# For loop
			if (LT==Compiler.LT_NONE and check_start(seq,i-1) and seq[i:].startswith(Compiler.FOR_LOOP_STRING)):
				i+=len(Compiler.FOR_LOOP_STRING)
				si=i-len(Compiler.FOR_LOOP_STRING)
				while (seq[i]==Compiler.SPACE_CHAR or seq[i]==Compiler.TAB_CHAR):
					i+=1
				if (seq[i]!=Compiler.FOR_COND_START_CHAR):
					i=si
				else:
					i+=1
					sli=li+0
					cd=[""]
					cdi=0
					b=0
					M=0
					while (b!=0 or len(cd)!=3 or seq[i]!=Compiler.FOR_COND_END_CHAR):
						cd[cdi]+=seq[i]
						if (seq[i]==Compiler.FOR_COND_START_CHAR):b+=1
						if (seq[i]==Compiler.FOR_COND_END_CHAR):b-=1
						if (seq[i]==Compiler.QUOTE_CHAR and ((i==0) or (i>0 and seq[i-1]!=Compiler.QUOTE_ESCAPE_CHAR))):
							if (M==0):
								M=1
							else:
								M=0
						if (seq[i]==Compiler.FOR_COND_DELIMETER):
							if (len(cd)==3):
								SyntaxError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Too many delimeters")
							cd[cdi]=cd[cdi][:-1]
							cd.append("")
							cdi+=1
						i+=1
						if (not (b==0 and len(cd)==3 and seq[i]==Compiler.FOR_COND_END_CHAR) and (i>=len(seq) or seq[i] in Compiler.LINE_BREAK_CHARS)):
							c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
							return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Expected '{Compiler.FOR_COND_END_CHAR}', found '{c}'")
					for j in range(1,3):
						if (cd[j][0]==Compiler.LINE_BREAK_ESCAPE_CHAR):
							cd[j]=cd[j][1:]
					ni=""
					b=0
					M=0
					j=0
					while (j<len(cd[2])):
						ni+=cd[2][j]
						if (seq[i]==Compiler.FOR_DEF_START_CHAR):b+=1
						if (seq[i]==Compiler.FOR_DEF_END_CHAR):b-=1
						if (seq[i]==Compiler.QUOTE_CHAR and ((j==0) or (j>0 and cd[2][j]!=Compiler.QUOTE_ESCAPE_CHAR))):
							if (M==0):
								M=1
							else:
								M=0
						if (b==0 and M==0 and cd[2][j]==Compiler.FOR_INCREMENT_DELIMETER):
							ni=ni[:-1]+Compiler.LINE_TERMINATOR_CHAR
						j+=1
					cd[2]=ni
					i+=1
					while (seq[i]==Compiler.SPACE_CHAR or seq[i]==Compiler.TAB_CHAR or seq[i] in Compiler.LINE_BREAK_CHARS):
						i+=1
					if (seq[i]!=Compiler.FOR_DEF_START_CHAR):
						c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
						return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Expected '{Compiler.FOR_DEF_START_CHAR}', found '{c}'")
					i+=1
					code=""
					b=1
					while (b!=0):
						code+=seq[i]
						if (seq[i]==Compiler.FOR_DEF_START_CHAR):b+=1
						if (seq[i]==Compiler.FOR_DEF_END_CHAR):b-=1
						if (b==0):
							code=code[:-1]
						i+=1
						if (i<len(seq) and seq[i]==Compiler.LINE_BREAK_CHAR):
							li+=1
						if (b!=0 and i>=len(seq)):
							c=seq[i-1].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
							return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Expected '{Compiler.FOR_DEF_END_CHAR}', found '{c}'")
					if (D==True):
						print("DEBUG \u2012 For loop")
					oVL=VL[:]
					cd[0]=Compiler.compile(Compiler.VAR_DEF_STRING+cd[0]+Compiler.LINE_TERMINATOR_CHAR,E=False,S=["FOR"],VL=VL[:],FL=FL[:],CL=CL[:])
					if (hasattr(cd[0],"ERROR") and cd[0].ERROR==True):
						cd[0].stack=S[:-1]+[[S[-1],sli+1,seq.split(Compiler.LINE_BREAK_CHAR)[sli+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]]
						return cd[0]
					for v in cd[0]:
						oVL.append(Variable(v["n"],v["r"],None))
					cd[1]=Compiler.compile_condition(cd[1],VL=oVL[:],FL=FL[:],CL=CL[:],S=S)
					if (hasattr(cd[1],"ERROR") and cd[1].ERROR==True):
						cd[1].stack=S[:-1]+[[S[-1],sli+1,seq.split(Compiler.LINE_BREAK_CHAR)[sli+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]]
						return cd[1]
					cd[2]=Compiler.compile(cd[2]+Compiler.LINE_TERMINATOR_CHAR,E=False,S=["FOR"],VL=oVL,FL=FL,CL=CL)
					if (hasattr(cd[2],"ERROR") and cd[2].ERROR==True):
						cd[2].stack=S[:-1]+[[S[-1],sli+1,seq.split(Compiler.LINE_BREAK_CHAR)[sli+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]]
						return cd[2]
					code=Compiler.compile(code,VL=oVL,FL=FL,CL=CL,S=S,E=False)
					if (hasattr(code,"ERROR") and code.ERROR==True):
						for i in range(0,len(code.stack)):
							code.stack[i][1]+=sli+1
							if (ntpath.isfile(code.stack[i][0])==True):
								break
						return code
					C+=[{"t":"for","d":cd[0],"c":cd[1],"i":cd[2],"s":code}]
					LT=Compiler.LT_FOR_LOOP
			# While loop
			if (LT==Compiler.LT_NONE and check_start(seq,i-1) and seq[i:].startswith(Compiler.WHILE_LOOP_STRING)):
				i+=len(Compiler.WHILE_LOOP_STRING)
				si=i-len(Compiler.WHILE_LOOP_STRING)
				while (seq[i]==Compiler.SPACE_CHAR or seq[i]==Compiler.TAB_CHAR):
					i+=1
				if (seq[i]!=Compiler.WHILE_COND_START_CHAR):
					i=si
				else:
					i+=1
					sli=li+0
					c=""
					b=0
					while (b!=0 or seq[i]!=Compiler.WHILE_COND_END_CHAR):
						c+=seq[i]
						if (seq[i]==Compiler.WHILE_COND_START_CHAR):b+=1
						if (seq[i]==Compiler.WHILE_COND_END_CHAR):b-=1
						i+=1
						if (not (b==0 and seq[i]==Compiler.WHILE_COND_END_CHAR) and (i>=len(seq) or seq[i] in Compiler.LINE_BREAK_CHARS)):
							c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
							return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Expected '{Compiler.WHILE_COND_END_CHAR}', found '{c}'")
					i+=1
					while (seq[i]==Compiler.SPACE_CHAR or seq[i]==Compiler.TAB_CHAR or seq[i] in Compiler.LINE_BREAK_CHARS):
						i+=1
					if (seq[i]!=Compiler.WHILE_DEF_START_CHAR):
						c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
						return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Expected '{Compiler.WHILE_DEF_START_CHAR}', found '{c}'")
					i+=1
					code=""
					b=1
					while (b!=0):
						code+=seq[i]
						if (seq[i]==Compiler.WHILE_DEF_START_CHAR):b+=1
						if (seq[i]==Compiler.WHILE_DEF_END_CHAR):b-=1
						if (b==0):
							code=code[:-1]
						i+=1
						if (i<len(seq) and seq[i]==Compiler.LINE_BREAK_CHAR):
							li+=1
						if (b!=0 and i>=len(seq)):
							c=seq[i-1].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
							return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Expected '{Compiler.WHILE_DEF_ENDT_CHAR}', found '{c}'")
					if (D==True):
						print("DEBUG \u2012 While loop")
					c=Compiler.compile_condition(c,VL=VL[:],FL=FL[:],CL=CL[:],S=S)
					if (hasattr(c,"ERROR") and c.ERROR==True):
						c.stack=S[:-1]+[[S[-1],sli+1,seq.split(Compiler.LINE_BREAK_CHAR)[sli+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]]
						return cd[1]
					code=Compiler.compile(code,VL=VL,FL=FL,CL=CL,S=S,E=False)
					if (hasattr(code,"ERROR") and code.ERROR==True):
						for i in range(0,len(code.stack)):
							code.stack[i][1]+=sli+1
							if (ntpath.isfile(code.stack[i][0])==True):
								break
						return code
					C+=[{"t":"while","c":c,"v":code}]
					LT=Compiler.LT_WHILE_LOOP
			# Function def
			if (LT==Compiler.LT_NONE and check_start(seq,i-1) and seq[i]==Compiler.VAR_TYPE_START_CHAR and seq[i+1:].split(Compiler.VAR_TYPE_END_CHAR)[0] in Compiler.ALLOWED_RETURN_VAR_TYPES):
				fn=""
				frt=seq[i+1:].split(Compiler.VAR_TYPE_END_CHAR)[0]
				params=[]
				code=""
				sdli=li+0
				i+=3+len(frt)
				if (seq[i:].startswith(Compiler.FUNC_DEF_STRING)):
					i+=len(Compiler.FUNC_DEF_STRING)
					sli=li+1
					if (seq[i] not in Compiler.ALLOWED_FUNC_NAME_START_CHARS):
						c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
						return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Function names cannot start with '{c}'")
					while (seq[i]!=Compiler.FUNC_PARAMS_START_CHAR):
						if (seq[i] not in Compiler.ALLOWED_FUNC_NAME_CHARS):
							c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
							return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Invalid function name chracter '{c}'")
						fn+=seq[i]
						i+=1
					for f in FL:
						if (f.name==fn and f.native==True):
							return OverrideError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],"Cannot override a native functions")
					i+=1
					while (seq[i]!=Compiler.FUNC_PARAMS_END_CHAR and seq[i-1]!=Compiler.FUNC_PARAMS_END_CHAR):
						if (seq[i]!=Compiler.SPACE_CHAR and seq[i]!=Compiler.TAB_CHAR):
							if (seq[i]!=Compiler.VAR_TYPE_START_CHAR):
								c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
								return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Expected '{Compiler.VAR_TYPE_START_CHAR}', found '{c}'")
							i+=1
							vn=""
							vt=""
							while (seq[i]!=Compiler.VAR_TYPE_END_CHAR):
								if (seq[i] not in Compiler.ALLOWED_VAR_TYPE_CHARS):
									c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
									return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Invalid variable type name character '{c}'")
								vt+=seq[i]
								i+=1
							if (vt not in Compiler.ALLOWED_VAR_TYPES):
								return TypeError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Unknown Type: '{vt}'")
							i+=1
							while (seq[i]==Compiler.SPACE_CHAR or seq[i]==Compiler.TAB_CHAR):
								i+=1
							if (seq[i] not in Compiler.ALLOWED_VAR_NAME_START_CHARS):
								c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
								return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Variables cannot start with '{c}'")
							while (seq[i]!=Compiler.FUNC_PARAMS_SPILT_CHAR and seq[i]!=Compiler.FUNC_PARAMS_END_CHAR):
								if (seq[i] not in Compiler.ALLOWED_VAR_NAME_CHARS):
									c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
									return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Invalid variable name character '{c}'")
								vn+=seq[i]
								i+=1
							params.append(Variable(vn,vt,"param"))
						i+=1
					for f in FL:
						if (f.name!=fn or len(f.params)!=len(params)):
							continue
						for p in f.params:
							for p2 in params:
								if (p.type!=p2.type):
									continue
						return OverrideError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],"Cannot declare the same function twice")
					if (seq[i-1]==Compiler.FUNC_PARAMS_END_CHAR):
						i+=1
					if (seq[i]==Compiler.LINE_BREAK_CHAR):
						li+=1
					while (seq[i]!=Compiler.FUNC_DEF_START_CHAR):
						if (seq[i]!=Compiler.SPACE_CHAR and seq[i]!=Compiler.TAB_CHAR and seq[i] not in Compiler.LINE_BREAK_CHARS):
							c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
							return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Expected '{Compiler.FUNC_DEF_START_CHAR}', found '{c}'")
						if (seq[i]==Compiler.LINE_BREAK_CHAR):
							li+=1
						i+=1
					i+=1
					b=1
					while (b!=0):
						if (seq[i]==Compiler.LINE_BREAK_CHAR):
							li+=1
						code+=seq[i]
						if (seq[i]==Compiler.FUNC_DEF_START_CHAR):b+=1
						if (seq[i]==Compiler.FUNC_DEF_END_CHAR):b-=1
						if (b==0):
							code=code[:-1]
						i+=1
						if (b!=0 and i>=len(seq)):
							c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
							return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Expected '{Compiler.FUNC_DEF_END_CHAR}', found '{c}'")
					LT=Compiler.LT_FUNC_DEF
					f=Function(fn,frt,params,code,FL[:],VL[:],CL[:])
					if (D==True):
						print("DEBUG \u2012 Func def")
					r=Compiler.compile(f.code,VL=f.get_vl(),FL=f.af+[f],CL=f.ac,S=S[:-1]+[[S[-1],sdli+1,seq.split("\n")[sdli+1]]]+[fn],E=False)
					if (hasattr(r,"ERROR") and r.ERROR==True):
						for i in range(0,len(r.stack)):
							if (ntpath.isfile(r.stack[i][0]) and i>=len(S)):
								break
							if (ntpath.isfile(r.stack[i][0])==False):
								r.stack[i][1]+=sdli+1
						return r
					f.code=r
					FL.append(f)
					pl=[]
					for k in params:
						pl+=[{"n":k.name,"t":k.type}]
					C+=[{"t":"f_def","n":fn,"r":frt,"p":pl,"v":r}]
			# Var def
			if (LT==Compiler.LT_NONE and check_start(seq,i-1) and seq[i:].startswith(Compiler.VAR_DEF_STRING)):
				i+=len(Compiler.VAR_DEF_STRING)
				if (D==True):
					print("DEBUG \u2012 Var def")
				while (seq[i] not in Compiler.LINE_BREAK_CHARS and seq[i]!=Compiler.LINE_TERMINATOR_CHAR and seq[i-1] not in Compiler.LINE_BREAK_CHARS and seq[i-1]!=Compiler.LINE_TERMINATOR_CHAR):
					if (seq[i]!=Compiler.VAR_TYPE_START_CHAR):
						c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
						return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Expected '{Compiler.VAR_TYPE_START_CHAR}', found '{c}'")
					i+=1
					vn=""
					vt=""
					while (seq[i]!=Compiler.VAR_TYPE_END_CHAR):
						if (seq[i] not in Compiler.ALLOWED_VAR_TYPE_CHARS):
							c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
							return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Invalid variable type name character '{c}'")
						vt+=seq[i]
						i+=1
					if (vt not in Compiler.ALLOWED_VAR_TYPES):
						return TypeError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Unknown Type: '{vt}'")
					i+=1
					while (seq[i]==Compiler.SPACE_CHAR or seq[i]==Compiler.TAB_CHAR):
						i+=1
					if (seq[i] not in Compiler.ALLOWED_VAR_NAME_START_CHARS):
						c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
						return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Variables cannot start with '{c}'")
					while (seq[i]!=Compiler.VAR_DEF_ASSIGN_CHAR and seq[i]!=Compiler.SPACE_CHAR and seq[i]!=Compiler.TAB_CHAR):
						if (seq[i] not in Compiler.ALLOWED_VAR_NAME_CHARS):
							c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
							return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Invalid variable name character '{c}'")
						vn+=seq[i]
						i+=1
					for vr in VL:
						if (vr.name==vn):
							return OverrideError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],"Cannot declare the same variable twice")
					while (seq[i]==Compiler.SPACE_CHAR or seq[i]==Compiler.TAB_CHAR):
						i+=1
					if (seq[i]!=Compiler.VAR_DEF_ASSIGN_CHAR):
						c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
						return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Expected '{Compiler.VAR_DEF_ASSIGN_CHAR}', found '{c}'")
					i+=1
					while (seq[i]==Compiler.SPACE_CHAR or seq[i]==Compiler.TAB_CHAR):
						i+=1
					args=""
					b=0
					while (not (b==0 and (seq[i]==Compiler.VAR_DEF_SPLIT_CHAR or seq[i] in Compiler.LINE_BREAK_CHARS or seq[i]==Compiler.LINE_TERMINATOR_CHAR))):
						args+=seq[i]
						if (seq[i]==Compiler.FUNC_PARAMS_START_CHAR):b+=1
						if (seq[i]==Compiler.FUNC_PARAMS_END_CHAR):b-=1
						i+=1
						if (b!=0 and i>=len(seq) or seq[i] in Compiler.LINE_BREAK_CHARS):
							c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
							return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Expected '{Compiler.VAR_DEF_SPLIT_CHAR}' or '{Compiler.LINE_TERMINATOR_CHAR}', found '{c}'")
					i+=1
					args=Compiler.compile_args([args],VL=VL,FL=FL,CL=CL,RT=[vt],S=S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],FN=vn)
					if (hasattr(args,"ERROR") and args.ERROR==True):
						args.l=li+1
						return args
					while (seq[i]==Compiler.SPACE_CHAR or seq[i]==Compiler.TAB_CHAR):
						i+=1
					VL.append(Variable(vn,vt,"null"))
					C+=[{"t":"v_def","n":vn,"r":vt,"v":args,"c":False}]
				LT=Compiler.LT_VAR_DEF
			# Const def
			if (LT==Compiler.LT_NONE and check_start(seq,i-1) and seq[i:].startswith(Compiler.CONST_DEF_STRING)):
				i+=len(Compiler.CONST_DEF_STRING)
				if (D==True):
					print("DEBUG \u2012 Const def")
				while (seq[i] not in Compiler.LINE_BREAK_CHARS and seq[i]!=Compiler.LINE_TERMINATOR_CHAR and seq[i-1] not in Compiler.LINE_BREAK_CHARS and seq[i-1]!=Compiler.LINE_TERMINATOR_CHAR):
					if (seq[i]!=Compiler.VAR_TYPE_START_CHAR):
						c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
						return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Expected '{Compiler.VAR_TYPE_START_CHAR}', found '{c}'")
					i+=1
					vn=""
					vt=""
					while (seq[i]!=Compiler.VAR_TYPE_END_CHAR):
						if (seq[i] not in Compiler.ALLOWED_VAR_TYPE_CHARS):
							c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
							return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Invalid variable type name character '{c}'")
						vt+=seq[i]
						i+=1
					if (vt not in Compiler.ALLOWED_VAR_TYPES):
						return TypeError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Unknown Type: '{vt}'")
					i+=1
					while (seq[i]==Compiler.SPACE_CHAR or seq[i]==Compiler.TAB_CHAR):
						i+=1
					if (seq[i] not in Compiler.ALLOWED_VAR_NAME_START_CHARS):
						c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
						return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Variables cannot start with '{c}'")
					while (seq[i]!=Compiler.VAR_DEF_ASSIGN_CHAR and seq[i]!=Compiler.SPACE_CHAR and seq[i]!=Compiler.TAB_CHAR):
						if (seq[i] not in Compiler.ALLOWED_VAR_NAME_CHARS):
							c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
							return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Invalid variable name character '{c}'")
						vn+=seq[i]
						i+=1
					for vr in VL:
						if (vr.name==vn):
							return OverrideError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],"Cannot declare the same variable twice")
					while (seq[i]==Compiler.SPACE_CHAR or seq[i]==Compiler.TAB_CHAR):
						i+=1
					if (seq[i]!=Compiler.VAR_DEF_ASSIGN_CHAR):
						c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
						return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Expected '{Compiler.VAR_DEF_ASSIGN_CHAR}', found '{c}'")
					i+=1
					while (seq[i]==Compiler.SPACE_CHAR or seq[i]==Compiler.TAB_CHAR):
						i+=1
					args=""
					b=0
					while (not (b==0 and (seq[i]==Compiler.VAR_DEF_SPLIT_CHAR or seq[i] in Compiler.LINE_BREAK_CHARS or seq[i]==Compiler.LINE_TERMINATOR_CHAR))):
						args+=seq[i]
						if (seq[i]==Compiler.FUNC_PARAMS_START_CHAR):b+=1
						if (seq[i]==Compiler.FUNC_PARAMS_END_CHAR):b-=1
						i+=1
						if (b!=0 and i>=len(seq) or seq[i] in Compiler.LINE_BREAK_CHARS):
							c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
							return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Expected '{Compiler.VAR_DEF_SPLIT_CHAR}' or '{Compiler.LINE_TERMINATOR_CHAR}', found '{c}'")
					i+=1
					args=Compiler.compile_args([args],VL=VL,FL=FL,CL=CL,RT=[vt],S=S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],FN=vn)
					if (hasattr(args,"ERROR") and args.ERROR==True):
						args.l=li+1
						return args
					while (seq[i]==Compiler.SPACE_CHAR or seq[i]==Compiler.TAB_CHAR):
						i+=1
					VL.append(Variable(vn,vt,"null",constant=True))
					C+=[{"t":"v_def","n":vn,"r":vt,"v":args,"c":True}]
				LT=Compiler.LT_VAR_DEF
			# Var assign
			if (LT==Compiler.LT_NONE and check_start(seq,i-1) and seq[i] in Compiler.ALLOWED_VAR_NAME_START_CHARS):
				nm=""
				si=i+0
				while (seq[i] in Compiler.ALLOWED_VAR_NAME_CHARS):
					nm+=seq[i]
					i+=1
					if (i>=len(seq) or seq[i] in Compiler.LINE_BREAK_CHARS):
						i=si
						nm=""
						break
				if (nm!=""):
					if (seq[i]!=Compiler.FUNC_PARAMS_START_CHAR and seq[i]!=Compiler.CLASS_ATTR_SPLIT_CHAR):
						v=None
						for tv in VL:
							if (tv.name==nm):
								v=tv
								break
						if (v is None):
							return SyntaxError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Unknown Variable: Unknown variable '{nm}'")
						if (seq[i]!=Compiler.VAR_DEF_ASSIGN_CHAR and seq[i+1]!=Compiler.VAR_DEF_ASSIGN_CHAR):
							c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
							return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Expected '{Compiler.VAR_DEF_ASSIGN_CHAR}', found '{c}'")
						if (seq[i]!=Compiler.VAR_DEF_ASSIGN_CHAR and seq[i] not in Compiler.OPERATORS):
							c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
							return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Expected any of '{Compiler.OPERATORS}' or '{Compiler.VAR_DEF_ASSIGN_CHAR}', found '{c}'")
						e=""
						if (seq[i]!=Compiler.VAR_DEF_ASSIGN_CHAR):
							e=nm+seq[i]+Compiler.OP_OPEN_BRACKET
							i+=1
						i+=1
						while (seq[i]!=Compiler.LINE_TERMINATOR_CHAR and seq[i] not in Compiler.LINE_BREAK_CHARS):
							e+=seq[i]
							i+=1
							if (i>=len(seq)):
								break
						if (e.startswith(nm)):
							e+=Compiler.OP_CLOSE_BRACKET
						if (v.constant==True):
							return ReassigmentError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Cannot override a constant")
						if (D==True):
							print("DEBUG \u2012 Var assign")
						c=Compiler.compile_args([e],S=S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],VL=VL,FL=FL,CL=CL,RT=[v.type],FN=nm)
						if (hasattr(c,"ERROR") and c.ERROR==True):
							return c
						C+=[{"t":"v_ass","n":nm,"e":c[0]}]
						LT=Compiler.LT_VAR_ASSIGN
					else:
						i=si
			# Class call
			if (LT==Compiler.LT_NONE and seq[i-1] not in Compiler.ALLOWED_FUNC_NAME_CHARS and seq[i-1] not in Compiler.ALLOWED_VAR_NAME_CHARS and seq[i] in Compiler.ALLOWED_CLASS_NAME_START_CHARS):
				cnms={}
				for c in CL:
					cnms[c.name]=c
				nm=""
				si=i+0
				while (seq[i]!=Compiler.CLASS_ATTR_SPLIT_CHAR):
					nm+=seq[i]
					i+=1
					if (i>=len(seq) or seq[i] in Compiler.LINE_BREAK_CHARS):
						nm=""
						break
				if (nm==""):
					i=si
				else:
					if (nm in cnms.keys()):
						cl=cnms[nm]
						i+=1
						fnm=""
						if (seq[i] not in Compiler.ALLOWED_FUNC_NAME_START_CHARS):
							c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
							return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Expected any of '{Compiler.ALLOWED_FUNC_NAME_START_CHARS}', found '{c}'")
						while (seq[i]!=Compiler.FUNC_PARAMS_START_CHAR):
							fnm+=seq[i]
							i+=1
							if (i>=len(seq) or seq[i] in Compiler.LINE_BREAK_CHARS):
								c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
								return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Expected '{Compiler.FUNC_PARAMS_START_CHAR}', found '{c}'")
						if (fnm not in cl.fl.keys()):
							return SyntaxError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Unknown Function: Unknown function '{nm}'")
						else:
							f=cl.fl[fnm]
							b=1
							i+=1
							c=[""]
							cci=0
							while (b!=0):
								if (seq[i] in Compiler.LINE_BREAK_CHARS):
									c=None
									break
								c[cci]+=seq[i]
								if (seq[i]==Compiler.FUNC_PARAMS_START_CHAR):b+=1
								if (seq[i]==Compiler.FUNC_PARAMS_END_CHAR):b-=1
								if (b==1 and seq[i]==Compiler.FUNC_PARAMS_SPILT_CHAR):
									c[cci]=c[cci][:-1]
									cci+=1
									c.append("")
								if (b==0):
									c[cci]=c[cci][:-1]
								i+=1
							if (c is None):
								c=seq[i].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
								return UnexpectedCharacterError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Expected '', found '{c}'")
							LT=Compiler.LT_CLASS_CALL
							ptl=None
							if (f.params!=None):
								ptl=[]
								for pr in f.params:
									ptl+=[pr.type]
							if (D==True):
								print("DEBUG \u2012 Func call")
							c=Compiler.compile_args(c,VL=VL,FL=FL,CL=CL,FN="Function "+nm+Compiler.CLASS_ATTR_SPLIT_CHAR+f.name,S=S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],RT=ptl)
							if (hasattr(c,"ERROR") and c.ERROR==True):
								c.l=li+1
								return c
							C.append({"t":"cf_call","c":nm,"v":fnm,"a":c})
					else:
						return SyntaxError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Unknown Function: Unknown function '{nm}'")
			# Func call
			if (LT==Compiler.LT_NONE and seq[i-1] not in Compiler.ALLOWED_FUNC_NAME_CHARS and seq[i-1] not in Compiler.ALLOWED_VAR_NAME_CHARS and seq[i] in Compiler.ALLOWED_FUNC_NAME_START_CHARS):
				fnms={}
				for f in FL:
					fnms[f.name]=f
				nm=""
				si=i+0
				while (seq[i]!=Compiler.FUNC_PARAMS_START_CHAR):
					nm+=seq[i]
					i+=1
					if (i>=len(seq) or seq[i] in Compiler.LINE_BREAK_CHARS):
						nm=""
						break
				if (nm==""):
					i=si
				else:
					if (nm in fnms.keys()):
						b=1
						i+=1
						c=[""]
						cci=0
						while (b!=0):
							if (seq[i] in Compiler.LINE_BREAK_CHARS):
								c=None
								break
							c[cci]+=seq[i]
							if (seq[i]==Compiler.FUNC_PARAMS_START_CHAR):b+=1
							if (seq[i]==Compiler.FUNC_PARAMS_END_CHAR):b-=1
							if (b==1 and seq[i]==Compiler.FUNC_PARAMS_SPILT_CHAR):
								c[cci]=c[cci][:-1]
								cci+=1
								c.append("")
							if (b==0):
								c[cci]=c[cci][:-1]
							i+=1
						if (c is None):
							i=si+1
						else:
							LT=Compiler.LT_FUNC_CALL
							f=fnms[nm]
							ptl=None
							if (f.params!=None):
								ptl=[]
								for pr in f.params:
									ptl+=[pr.type]
							if (D==True):
								print("DEBUG \u2012 Func call")
							c=Compiler.compile_args(c,VL=VL,FL=FL,CL=CL,FN="Function "+f.name,S=S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],RT=ptl)
							if (hasattr(c,"ERROR") and c.ERROR==True):
								c.l=li+1
								return c
							C.append({"t":"f_call","v":f.name,"a":c})
					else:
						return SyntaxError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Unknown Function: Unknown function '{nm}'")
			# Line end
			if (i<len(seq) and seq[i] in Compiler.LINE_BREAK_CHARS):
				if (LT==Compiler.LT_NONE):
					return SyntaxError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Unknown error")
				if (LT!=Compiler.LT_EMPTY and LT!=Compiler.LT_COMMENT and LT!=Compiler.LT_FUNC_DEF and LT!=Compiler.LT_IF_STATEMENT and LT!=Compiler.LT_FOR_LOOP and LT!=Compiler.LT_WHILE_LOOP and seq[i-1]!=Compiler.LINE_TERMINATOR_CHAR):
					c=seq[i-1].replace(Compiler.LINE_BREAK_CHAR,"\\n").replace(Compiler.TAB_CHAR,"\\t")
					return SyntaxError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Unterminated Line: Expected '{Compiler.LINE_TERMINATOR_CHAR}', found '{c}'")
				if (M==Compiler.M_STRING):
					return SyntaxError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],"Unterminated string")
				if (seq[i]==Compiler.LINE_BREAK_CHAR):
					li+=1
				LT=Compiler.LT_NONE
			i+=1
		if (len(BR)>0):
			return BracketError(S[:-1]+[[S[-1],li+1,seq.split(Compiler.LINE_BREAK_CHAR)[li+1].replace(Compiler.LINE_BREAK_ESCAPE_CHAR,"")]],f"Found '{BR[0]}' without a pair")
		if (E==False):
			return C
		if (E==True and D==True):
			print(f"DEBUG \u2012 Compiling took {(int((time.time()-ST)*1000)+1)/1000}s")
		return pickle.dumps(json.dumps(C,sort_keys=True,separators=(",",":")))



	@staticmethod
	def compile_args(c,VL=[],FL=[],CL=[],RT=None,FN="Function f",S=[]):
		r=[]
		C=[]
		for seq in c:
			t1=None
			t2=None
			op=None
			i=0
			M=False
			A=[]
			while (i<len(seq)):
				if (seq[i]==Compiler.OP_OPEN_BRACKET):
					s=""
					i+=1
					b=1
					while (b!=0):
						if (seq[i]==Compiler.OP_OPEN_BRACKET):b+=1
						if (seq[i]==Compiler.OP_CLOSE_BRACKET):b-=1
						if (b!=0):
							s+=seq[i]
						i+=1
						if (b!=0 and i>=len(seq)):
							return BracketError(S,f"Found '{Compiler.OP_OPEN_BRACKET}' without a pair")
					e=Compiler.compile_args([s],VL=VL,FL=FL,CL=CL,FN=FN,S=S)
					if (hasattr(e,"ERROR") and e.ERROR==True):
						return e
					A+=[{"t":"brackets","v":e[0]}]
					if (i>=len(seq)):
						break
				if (((i>0 and seq[i-1] not in Compiler.ALLOWED_VAR_NAME_CHARS and seq[i-1] not in Compiler.ALLOWED_TYPE_FLOAT_CHARS) or i==0) and (seq[i:].startswith(Compiler.VAR_TYPE_BOOL_TRUE) or seq[i:].startswith(Compiler.VAR_TYPE_BOOL_FALSE))):
					if (seq[i:].startswith(Compiler.VAR_TYPE_BOOL_TRUE) and ((i+len(Compiler.VAR_TYPE_BOOL_TRUE)<len(seq) and seq[i+len(Compiler.VAR_TYPE_BOOL_TRUE)] not in Compiler.ALLOWED_VAR_NAME_CHARS and seq[i+len(Compiler.VAR_TYPE_BOOL_TRUE)] not in Compiler.ALLOWED_TYPE_FLOAT_CHARS) or (i+len(Compiler.VAR_TYPE_BOOL_TRUE)>=len(seq)))):
						t1=t2
						t2="bool"
						i+=len(Compiler.VAR_TYPE_BOOL_TRUE)
						M=True
						A+=[{"t":"bool","v":True}]
					if (seq[i:].startswith(Compiler.VAR_TYPE_BOOL_FALSE) and ((i+len(Compiler.VAR_TYPE_BOOL_FALSE)<len(seq) and seq[i+len(Compiler.VAR_TYPE_BOOL_FALSE)] not in Compiler.ALLOWED_VAR_NAME_CHARS and seq[i+len(Compiler.VAR_TYPE_BOOL_FALSE)] not in Compiler.ALLOWED_TYPE_FLOAT_CHARS) or (i+len(Compiler.VAR_TYPE_BOOL_FALSE)>=len(seq)))):
						t1=t2
						t2="bool"
						i+=len(Compiler.VAR_TYPE_BOOL_FALSE)
						M=True
						A+=[{"t":"bool","v":False}]
				if (((i>0 and seq[i-1] not in Compiler.ALLOWED_VAR_NAME_CHARS and seq[i-1] not in Compiler.ALLOWED_TYPE_FLOAT_CHARS) or i==0) and seq[i]==Compiler.QUOTE_CHAR):
					i+=1
					nm=""
					while (True):
						if (seq[i-1]!=Compiler.QUOTE_ESCAPE_CHAR and seq[i]==Compiler.QUOTE_CHAR):
							break
						nm+=seq[i]
						i+=1
						if (i>=len(seq)):
							return SyntaxError(S,"Unterminated string")
					t1=t2
					t2="string"
					M=True
					A+=[{"t":"string","v":nm.replace("\\n","\n").replace("\\t","\t").replace("\\\"","\"")}]
				if (((i>0 and seq[i-1] not in Compiler.ALLOWED_VAR_NAME_CHARS and seq[i-1] not in Compiler.ALLOWED_TYPE_FLOAT_CHARS) or i==0) and seq[i] in Compiler.ALLOWED_CLASS_NAME_START_CHARS):
					si=i+0
					if (i>0 and seq[i-1]==Compiler.FUNC_PARAMS_END_CHAR):
						op=Compiler.OP_MULT
						A+=[{"t":"operator","v":op}]
					nm=""
					while (seq[i]!=Compiler.CLASS_ATTR_SPLIT_CHAR):
						nm+=seq[i]
						i+=1
						if (((i<len(seq) and seq[i]!=Compiler.CLASS_ATTR_SPLIT_CHAR) or (i>=len(seq))) and (i>=len(seq) or seq[i] not in Compiler.ALLOWED_CLASS_NAME_CHARS)):
							nm=None
							break
					if (nm is None):
						i=si
					else:
						i+=1
						cl=None
						for tc in CL:
							if (tc.name==nm):
								cl=tc
								break
						if (cl is None):
							return SyntaxError(S,f"Unknown Class: Class '{nm}' doesn't exist")
						#############################
						fnm=""
						while (seq[i] in Compiler.ALLOWED_VAR_NAME_CHARS):
							fnm+=seq[i]
							i+=1
							if (i>=len(seq)):
								break
						if (i<len(seq) and seq[i]==Compiler.FUNC_PARAMS_START_CHAR):
							f=None
							for cf in cl.fl.values():
								if (cf.name==fnm):
									f=cf
									break
							if (f is None):
								return SyntaxError(S,f"Unknown Function: Function '{fnm}' doesn't exist")
							p=[""]
							pi=0
							b=1
							i+=1
							while(b!=0):
								if (seq[i]==Compiler.FUNC_PARAMS_START_CHAR):b+=1
								if (seq[i]==Compiler.FUNC_PARAMS_END_CHAR):b-=1
								p[pi]+=seq[i]
								if (b==1 and seq[i]==Compiler.FUNC_PARAMS_SPILT_CHAR):
									p[pi]=p[pi][:-1]
									pi+=1
									p.append("")
								if (b==0):
									p[pi]=p[pi][:-1]
								i+=1
								if (b!=0 and i>=len(seq)):
									return BracketError(S,f"Found '{Compiler.FUNC_PARAMS_START_CHAR}' without a pair")
							ptl=[]
							if (f.params is None):
								ptl=None
							else:
								for k in f.params:
									ptl+=[k.type]
							p=Compiler.compile_args(p,VL=VL,FL=FL,CL=CL,RT=ptl,FN="Function "+cl.name+Compiler.CLASS_ATTR_SPLIT_CHAR+f.name,S=S)
							if (hasattr(p,"ERROR") and p.ERROR==True):
								return p
							i-=1
							t1=t2
							t2=f.r_type
							M=True
							A+=[{"t":"cf_call","c":nm,"v":f.name,"a":p}]
						#############################
				if (((i>0 and seq[i-1] not in Compiler.ALLOWED_VAR_NAME_CHARS and seq[i-1] not in Compiler.ALLOWED_TYPE_FLOAT_CHARS) or i==0) and seq[i] in Compiler.ALLOWED_VAR_NAME_START_CHARS):
					if (i>0 and seq[i-1]==Compiler.FUNC_PARAMS_END_CHAR):
						op=Compiler.OP_MULT
						A+=[{"t":"operator","v":op}]
					nm=""
					while (seq[i] in Compiler.ALLOWED_VAR_NAME_CHARS):
						nm+=seq[i]
						i+=1
						if (i>=len(seq)):
							break
					if (i<len(seq) and seq[i]==Compiler.FUNC_PARAMS_START_CHAR):
						f=None
						for cf in FL:
							if (cf.name==nm):
								f=cf
								break
						if (f is None):
							return SyntaxError(S,f"Unknown Function: Function '{nm}' doesn't exist")
						p=[""]
						pi=0
						b=1
						i+=1
						while(b!=0):
							if (seq[i]==Compiler.FUNC_PARAMS_START_CHAR):b+=1
							if (seq[i]==Compiler.FUNC_PARAMS_END_CHAR):b-=1
							p[pi]+=seq[i]
							if (b==1 and seq[i]==Compiler.FUNC_PARAMS_SPILT_CHAR):
								p[pi]=p[pi][:-1]
								pi+=1
								p.append("")
							if (b==0):
								p[pi]=p[pi][:-1]
							i+=1
							if (b!=0 and i>=len(seq)):
								return BracketError(S,f"Found '{Compiler.FUNC_PARAMS_START_CHAR}' without a pair")
						ptl=[]
						if (f.params is None):
							ptl=None
						else:
							for k in f.params:
								ptl+=[k.type]
						p=Compiler.compile_args(p,VL=VL,FL=FL,CL=CL,RT=ptl,FN="Function "+f.name,S=S)
						if (hasattr(p,"ERROR") and p.ERROR==True):
							return p
						i-=1
						t1=t2
						t2=f.r_type
						M=True
						A+=[{"t":"f_call","v":f.name,"a":p}]
					else:
						for v in VL:
							if (v.name==nm):
								nm=None
								break
						if (nm!=None):
							return SyntaxError(S,f"Unknown Variable: Variable '{nm}' doesn't exist")
						i-=1
						t1=t2
						t2=v.type
						M=True
						A+=[{"t":"v_ref","v":v.name}]
				if (((i>0 and seq[i-1] not in Compiler.ALLOWED_VAR_NAME_CHARS and seq[i-1] not in Compiler.ALLOWED_TYPE_FLOAT_CHARS) or i==0) and seq[i] in Compiler.ALLOWED_TYPE_FLOAT_START_CHARS):
					nm=""
					t="int"
					while (seq[i] in Compiler.ALLOWED_TYPE_FLOAT_CHARS or seq[i]==Compiler.TYPE_FLOAT_SPLIT_CHAR):
						nm+=seq[i]
						if (seq[i]==Compiler.TYPE_FLOAT_SPLIT_CHAR):
							if (t=="float"):
								return UnexpectedCharacterError(S,f"Expected any of '{Compiler.ALLOWED_TYPE_FLOAT_CHARS}', found '{seq[i]}'")
							t="float"
						i+=1
						if (i>=len(seq)):
							break
					i-=1
					t1=t2
					t2=t
					M=True
					v=0
					if (t=="int"):
						m=1
						for d in nm[::-1]:
							v+=int(d)*m
							m*=10
					else:
						m=1
						for d in nm.split(".")[0][::-1]:
							if (d=="_"):
								continue
							v+=int(d)*m
							m*=10
						m=0.1
						for d in nm.split(".")[1]:
							if (d=="_"):
								continue
							v+=int(d)*m
							m/=10
					A+=[{"t":t,"v":v}]
				if (i<len(seq) and seq[i] in Compiler.OPERATORS):
					if (op!=None):
						return UnexpectedCharacterError(S,f"Expected a variable or a function, found '{seq[i]}'")
					if (seq[i]==Compiler.OP_ADD):
						op=Compiler.OP_ADD
					if (seq[i]==Compiler.OP_SUB):
						op=Compiler.OP_SUB
					if (seq[i]==Compiler.OP_MULT):
						op=Compiler.OP_MULT
					if (seq[i]==Compiler.OP_DIV):
						op=Compiler.OP_DIV
					if (seq[i]==Compiler.OP_MOD):
						op=Compiler.OP_MOD
					if (seq[i]==Compiler.OP_POW):
						op=Compiler.OP_POW
					if (op is None):
						return UnsupportedOperatorError(S,f"Unknown operator '{seq[i]}'")
					M=True
					A+=[{"t":"operator","v":op}]
				if (t1!=None and t2!=None):
					if (op==Compiler.OP_ADD):
						if ((t1=="int" or t1=="float") and (t2=="int" or t2=="float")):
							t1=None
							if (t1=="float" or t2=="float"):
								t2="float"
							else:
								t2="int"
						if (((t1=="int" or t1=="float") and t2=="string") or (t1=="string" and (t2=="int" or t2=="float"))):
							t1=None
							t2="string"
						if (t1=="string" and t2=="string"):
							t1=None
							t2="string"
					if (op==Compiler.OP_SUB):
						if ((t1=="int" or t1=="float") and (t2=="int" or t2=="float")):
							t1=None
							if (t1=="float" or t2=="float"):
								t2="float"
							else:
								t2="int"
					if (op==Compiler.OP_MULT):
						if ((t1=="int" or t1=="float") and (t2=="int" or t2=="float")):
							t1=None
							if (t1=="float" or t2=="float"):
								t2="float"
							else:
								t2="int"
						if ((t1=="int" and t2=="string") or (t1=="string" and t2=="int")):
							t1=None
							t2="string"
					if (op==Compiler.OP_DIV):
						if ((t1=="int" or t1=="float") and (t2=="int" or t2=="float")):
							t1=None
							t2="float"
					if (op==Compiler.OP_MOD):
						if ((t1=="int" or t1=="float") and (t2=="int" or t2=="float")):
							t1=None
							if (t1=="float" or t2=="float"):
								t2="float"
							else:
								t2="int"
					if (op==Compiler.OP_POW):
						if ((t1=="int" or t1=="float") and (t2=="int" or t2=="float")):
							t1=None
							if (t1=="float" or t2=="float"):
								t2="float"
							else:
								t2="int"
					op=None
					if (t1!=None):
						return UnsupportedOperatorError(S,f"Unsupported operator '{op}' for '{t1}' and '{t2}'")
					M=True
				if (M==False and ((i<len(seq) and seq[i]!=Compiler.SPACE_CHAR and seq[i]!=Compiler.TAB_CHAR) or (i>=len(seq)))):
					return UnexpectedCharacterError(S,f"Unexpected character '{seq[i] if i<len(seq) else seq[i-1]}'")
				M=False
				i+=1
			r.append(t2)
			C+=[A]
		if (RT is not None and not ((len(r)==1 and r[0] is None) or (len(r)>1))):
			l1=""
			if (len(RT)>=1 and RT[0]!=""):
				for k in RT:
					if (k!=None):
						l1+=f"<{k}>, "
					else:
						l1+=f"<any>, "
				l1=l1[:-2]
			l2=""
			if (len(c)>=1 and c[0]!=""):
				for k in r:
					if (k!=None):
						l2+=f"<{k}>, "
					else:
						l2+=f"null, "
				l2=l2[:-2]
			if (len(r)!=len(RT)):
				if (FN.startswith("Function")):
					return ArgumentError(S,f"{FN}({l1}) is not applicable for the arguments ({l2})")
				else:
					return ArgumentError(S,f"Variable {l1.split(', ')[0]}{FN} is not applicable for {l2.split(', ')[0]}")
			i=0
			while (i<len(r)):
				if (RT[i] is None):
					i+=1
					continue
				if ((r[i]=="float" or r[i]=="int") and (RT[i]=="float" or RT[i]=="int")):
					r[i]=RT[i]
				if (r[i]!=RT[i]):
					if (FN.startswith("Function")):
						return ArgumentError(S,f"{FN}({l1}) is not applicable for the arguments ({l2})")
					else:
						return ArgumentError(S,f"Variable {l1.split(', ')[0]}{FN} is not applicable for {l2.split(', ')[0]}")
				i+=1
		return C



	@staticmethod
	def compile_condition(seq,VL=[],FL=[],CL=[],S=[]):
		i=0
		c=[[""]]
		ci=0
		cj=0
		b=0
		M=0
		while (i<len(seq)):
			if (seq[i]==Compiler.COND_OPEN_BRACKETS):b+=1
			if (seq[i]==Compiler.COND_CLOSE_BRACKETS):b-=1
			if (seq[i]==Compiler.QUOTE_CHAR and ((i==0) or (i>0 and seq[i-1]!=Compiler.QUOTE_ESCAPE_CHAR))):
				if (M==0):
					M=1
				else:
					M=0
			if (M==0 and b==0 and seq[i:].startswith(Compiler.COND_AND_CHAR)):
				if (len(c[ci])==1 and c[ci][0]==""):
					return UnexpectedCharacterError(S,f"Expected a condition, found '{Compiler.COND_AND_CHAR}'")
				i+=len(Compiler.COND_AND_CHAR)
				c.append({"t":"and"})
				ci+=2
				cj=0
				c.append([""])
			elif (M==0 and b==0 and seq[i:].startswith(Compiler.COND_OR_CHAR)):
				if (len(c[ci])==1 and c[ci][0]==""):
					return UnexpectedCharacterError(S,f"Expected a condition, found '{Compiler.COND_OR_CHAR}'")
				i+=len(Compiler.COND_OR_CHAR)
				c.append({"t":"or"})
				ci+=2
				cj=0
				c.append([""])
			elif (M==0 and b==0 and seq[i:].startswith(Compiler.COND_EQ_CHAR)):
				if (c[ci][cj]==""):
					return UnexpectedCharacterError(S,f"Expected a condition, found '{Compiler.COND_EQ_CHAR}'")
				i+=len(Compiler.COND_EQ_CHAR)
				c[ci].append({"t":Compiler.COND_EQ_CHAR})
				cj+=2
				c[ci].append("")
			elif (M==0 and b==0 and seq[i:].startswith(Compiler.COND_NOT_EQ_CHAR)):
				if (c[ci][cj]==""):
					return UnexpectedCharacterError(S,f"Expected a condition, found '{Compiler.COND_NOT_EQ_CHAR}'")
				i+=len(Compiler.COND_NOT_EQ_CHAR)
				c[ci].append({"t":Compiler.COND_NOT_EQ_CHAR})
				cj+=2
				c[ci].append("")
			elif (M==0 and b==0 and seq[i:].startswith(Compiler.COND_NOT_LESS_CHAR)):
				if (c[ci][cj]==""):
					return UnexpectedCharacterError(S,f"Expected a condition, found '{Compiler.COND_NOT_LESS_CHAR}'")
				i+=len(Compiler.COND_NOT_LESS_CHAR)
				c[ci].append({"t":Compiler.COND_NOT_LESS_CHAR})
				cj+=2
				c[ci].append("")
			elif (M==0 and b==0 and seq[i:].startswith(Compiler.COND_NOT_MORE_CHAR)):
				if (c[ci][cj]==""):
					return UnexpectedCharacterError(S,f"Expected a condition, found '{Compiler.COND_NOT_MORE_CHAR}'")
				i+=len(Compiler.COND_NOT_MORE_CHAR)
				c[ci].append({"t":Compiler.COND_NOT_MORE_CHAR})
				cj+=2
				c[ci].append("")
			elif (M==0 and b==0 and seq[i:].startswith(Compiler.COND_LESS_CHAR)):
				if (c[ci][cj]==""):
					return UnexpectedCharacterError(S,f"Expected a condition, found '{Compiler.COND_LESS_CHAR}'")
				i+=len(Compiler.COND_LESS_CHAR)
				c[ci].append({"t":Compiler.COND_LESS_CHAR})
				cj+=2
				c[ci].append("")
			elif (M==0 and b==0 and seq[i:].startswith(Compiler.COND_MORE_CHAR)):
				if (c[ci][cj]==""):
					return UnexpectedCharacterError(S,f"Expected a condition, found '{Compiler.COND_MORE_CHAR}'")
				i+=len(Compiler.COND_MORE_CHAR)
				c[ci].append({"t":Compiler.COND_MORE_CHAR})
				cj+=2
				c[ci].append("")
			else:
				if (i<len(seq)):
					c[ci][cj]+=seq[i]
				i+=1
		i=0
		for i in range(0,len(c)):
			if (type(c[i])==dict):
				continue
			for j in range(0,len(c[i])):
				seq=c[i][j]
				if (type(seq)!=str):
					continue
				if (seq[0]==Compiler.COND_OPEN_BRACKETS):
					k=1
					b=1
					s=""
					while (b!=0):
						s+=seq[k]
						if (seq[k]==Compiler.COND_OPEN_BRACKETS):b+=1
						if (seq[k]==Compiler.COND_CLOSE_BRACKETS):b-=1
						if (b==0):
							s=s[:-1]
						k+=1
					r=Compiler.compile_condition(s,VL=VL,FL=FL,CL=CL,S=S)
					if (len(r)==1 and len(r[0])==1 and r[0][0]==s):
						c[i][j]=s
					else:
						c[i][j]=r
				elif (type(seq)==str):
					c[i][j]=Compiler.compile_args([seq],VL=VL,FL=FL,CL=CL,S=S)
					if (hasattr(c[i][j],"ERROR") and c[i][j].ERROR==True):
						return c[i][j]
			if (len(c[i])==1):
				c[i]+=[{"t":"=="},[[{"t":"bool","v":True}]]]
		return c



	@staticmethod
	def unicode(v,t):
		if (t!="string"):
			return v
		r=""
		i=0
		while (i<len(v)):
			if (v[i:].startswith(Compiler.UNICODE_ESCAPE_STRING)):
				i+=len(Compiler.UNICODE_ESCAPE_STRING)
				us=v[i:i+Compiler.UNICODE_ESCAPE_LENGTH]
				i+=Compiler.UNICODE_ESCAPE_LENGTH-1
				r+=eval(f"\"\\u{us}\"")
			else:
				r+=v[i]
			i+=1
		return r



	@staticmethod
	def run(seq,VL=[],_FL=[],CL=[],GCL=False):
		if (type(seq)==bytes):
			seq=json.loads(pickle.loads(seq))
		FL=_FL[:]
		fnl=[]
		for f in FL:
			fnl.append(f.name)
		for k in BUILTIN_FUNCTION_LIST:
			if (k.name not in fnl):
				FL.append(k)
		for cmd in seq:
			if (cmd["t"]=="f_def"):
				pl=[]
				for p in cmd["p"]:
					pl.append(Variable(p["n"],p["t"],"param"))
				FL.append(Function(cmd["n"],cmd["r"],pl,cmd["v"],FL[:],VL[:],CL[:]))
			elif (cmd["t"]=="v_def"):
				VL.append(Variable(cmd["n"],cmd["r"],Compiler.unicode(Compiler.eval_params(cmd["v"],VL=VL,FL=FL,CL=CL)[0].value,cmd["r"]),constant=cmd["c"]))
			elif (cmd["t"]=="f_call"):
				for f in FL:
					if (f.name==cmd["v"]):
						al=Compiler.eval_params(cmd["a"],VL=VL,FL=FL+[f],CL=CL)
						if (hasattr(f,"exec")):
							f.exec(al)
						else:
							Compiler.run(f.code,VL=f.get_vl(params=al),FL=f.af[:]+[f],CL=f.ac[:])
						break
			elif (cmd["t"]=="cf_call"):
				for c in CL:
					if (c.name==cmd["c"]):
						f=c.fl[cmd["v"]]
						al=Compiler.eval_params(cmd["a"],VL=VL,FL=FL+[f],CL=CL)
						if (hasattr(f,"exec")):
							f.exec(al)
						else:
							Compiler.run(f.code,VL=f.get_vl(params=al),FL=f.af[:]+[f],CL=f.ac[:])
						break
			elif (cmd["t"]=="v_ass"):
				for v in VL:
					if (v.name==cmd["n"]):
						v.value=Compiler.eval_params([cmd["e"]],VL=VL,FL=FL,CL=CL)[0].value
			elif (cmd["t"]=="if_c"):
				if (Compiler.eval_cond(cmd["c"],VL=VL,FL=FL,CL=CL)==True):
					Compiler.run(cmd["v"],VL=VL[:],FL=FL[:],CL=CL[:])
				else:
					if (cmd["e"]!=None):
						Compiler.run(cmd["e"],VL=VL[:],FL=FL[:],CL=CL[:])
			elif (cmd["t"]=="for"):
				oVL=VL[:]
				Compiler.run(cmd["d"],VL=oVL,FL=FL,CL=CL)
				while (True):
					if (Compiler.eval_cond(cmd["c"],VL=oVL,FL=FL,CL=CL)==False):
						break
					Compiler.run(cmd["s"],VL=oVL,FL=FL,CL=CL)
					Compiler.run(cmd["i"],VL=oVL,FL=FL,CL=CL)
			elif (cmd["t"]=="while"):
				while (True):
					if (Compiler.eval_cond(cmd["c"],VL=VL,FL=FL,CL=CL)==False):
						break
					Compiler.run(cmd["v"],VL=VL,FL=FL,CL=CL)
			elif (cmd["t"]=="imp"):
				if (cmd["o"]=="p"):
					data=None
					with open(cmd["d"]) as f:
						data=json.loads(f.read())
					tmp=shutil.copy(cmd["v"],ntpath.join(ntpath.split(__file__)[0],TEMP_FOLDER_PATH)+"_"+cmd["n"]+Compiler.IMPORT_MODULE_PYTHON_EXT)
					m=importlib.import_module("_"+cmd["n"])
					fl=[]
					for f in data["functions"]:
						pl=[]
						if (f["params"] is None):
							pl=None
						else:
							for k in f["params"]:
								pl+=[Variable("",k,"param")]
						nf=Function(f["name"],f["return_type"],pl,"",[],[],[])
						setattr(nf,"import_",getattr(m,f["func_name"]))
						setattr(nf,"exec",getattr(nf,"_e"))
						fl.append(nf)
					os.remove(tmp)
					CL.append(Class(cmd["n"],fl))
				else:
					data=""
					with open(cmd["v"],"r") as f:
						data=f.read()
					r=Compiler.compile(data,S=[cmd["v"]],E=False)
					if (hasattr(r,"ERROR") and r.ERROR==True):
						write_warn(r.print()+"\n")
					else:
						icl=[]
						for k in r:
							if (k["t"]=="imp"):
								icl+=Compiler.run([k],VL=[],FL=[],CL=[],GCL=True)
						fl=[]
						for k in r:
							if (k["t"]=="f_def"):
								pl=[]
								for pr in k["p"]:
									pl+=[Variable(pr["n"],pr["t"],"param")]
								fl+=[Function(k["n"],k["r"],pl,k["v"],BUILTIN_FUNCTION_LIST,[],icl[:])]
						CL.append(Class(cmd["n"],fl))
			else:
				write_warn("\nUNKNOWN COMMAND: "+str(cmd)+"\n")
		if (GCL==True):
			return CL
		return None



	@staticmethod
	def eval_params(c,VL=[],FL=[],CL=[],L=None):
		if (L is None):
			L=Compiler.MAX_OP_LVL
		r=[]
		for seq in c:
			tv=None
			i=0
			ar=[]
			if (type(seq)==Variable):
				r.append(seq)
				continue
			for e in seq:
				tv=None
				if (type(e)==Variable):
					tv=e
				else:
					if (e["t"]!="operator" and e["t"]!="f_call" and e["t"]!="brackets" and e["t"]!="cf_call"):
						if (e["t"]=="v_ref"):
							for v in VL:
								if (v.name==e["v"]):
									tv=Variable("",v.type,Compiler.unicode(v.value,v.type))
									break
						else:
							tv=Variable("",e["t"],Compiler.unicode(e["v"],e["t"]))
					elif (e["t"]=="f_call"):
						for f in FL:
							if (f.name==e["v"]):
								al=Compiler.eval_params(e["a"],VL=VL,FL=FL,CL=CL)
								if (hasattr(f,"exec")):
									tv=f.exec(al)
								else:
									tv=Compiler.run(f.code,VL=f.get_vl(params=al),FL=f.af+[f],CL=f.ac)
					elif (e["t"]=="cf_call"):
						for c in CL:
							if (c.name==e["c"]):
								f=c.fl[e["v"]]
								al=Compiler.eval_params(e["a"],VL=VL,FL=FL,CL=CL)
								if (hasattr(f,"exec")):
									tv=f.exec(al)
								else:
									tv=Compiler.run(f.code,VL=f.get_vl(params=al),FL=f.af+[f],CL=f.ac)
					elif (e["t"]=="brackets"):
						tv=Compiler.eval_params([e["v"]],VL=VL,FL=FL,CL=CL)[0]
					elif (e["t"]=="operator"):
						pass
					else:
						write_warn("UNKNOWN SUB-COMMAND: "+str(e)+"\n")
				if (tv!=None):
					if (i>1):
						if (seq[i-1]["v"] not in getattr(Compiler,"OP_LVL_"+str(L))):
							ar.append(seq[i-1])
							ar.append(tv)
						else:
							o=ar[-1]
							t1=o.type
							t2=tv.type
							if (seq[i-1]["v"]==Compiler.OP_ADD):
								if ((t1=="int" or t1=="float") and (t2=="int" or t2=="float")):
									if (t1=="float" or t2=="float"):
										o=Variable("","float",o.value+tv.value)
									else:
										o=Variable("","int",o.value+tv.value)
								if (((t1=="int" or t1=="float") and t2=="string") or (t1=="string" and (t2=="int" or t2=="float"))):
									o=Variable("","string",str(o.value)+str(tv.value))
								if (t1=="string" and t2=="string"):
									o=Variable("","string",o.value+tv.value)
							if (seq[i-1]["v"]==Compiler.OP_SUB):
								if ((t1=="int" or t1=="float") and (t2=="int" or t2=="float")):
									if (t1=="float" or t2=="float"):
										o=Variable("","float",o.value-tv.value)
									else:
										o=Variable("","int",o.value-tv.value)
							if (seq[i-1]["v"]==Compiler.OP_MULT):
								if ((t1=="int" or t1=="float") and (t2=="int" or t2=="float")):
									if (t1=="float" or t2=="float"):
										o=Variable("","float",o.value*tv.value)
									else:
										o=Variable("","int",o.value*tv.value)
								if ((t1=="int" and t2=="string") or (t1=="string" and t2=="int")):
									if (t1=="string"):
										s=""
										for _ in range(0,tv.value):
											s+=o.value
										o=Variable("","string",Compiler.unicode(s,"string"))
									else:
										s=""
										for _ in range(0,o.value):
											s+=tv.value
										o=Variable("","string",Compiler.unicode(s,"string"))
							if (seq[i-1]["v"]==Compiler.OP_DIV):
								if ((t1=="int" or t1=="float") and (t2=="int" or t2=="float")):
									o=Variable("","float",o.value/tv.value)
							if (seq[i-1]["v"]==Compiler.OP_MOD):
								if ((t1=="int" or t1=="float") and (t2=="int" or t2=="float")):
									if (t1=="float" or t2=="float"):
										o=Variable("","float",o.value%tv.value)
									else:
										o=Variable("","int",o.value%tv.value)
							if (seq[i-1]["v"]==Compiler.OP_POW):
								if ((t1=="int" or t1=="float") and (t2=="int" or t2=="float")):
									t1=None
									if (t1=="float" or t2=="float"):
										o=Variable("","float",o.value**tv.value)
									else:
										o=Variable("","int",o.value**tv.value)
							ar[-1]=o
					else:
						ar.append(tv)
				i+=1
			if (len(ar)==1):ar=ar[0]
			r.append(ar)
		if (L-1==0):
			return r
		return Compiler.eval_params(r,VL=VL,FL=FL,CL=CL,L=L-1)



	@staticmethod
	def eval_cond(seq,VL=[],FL=[],CL=[]):
		O=None
		for i in range(0,len(seq)):
			if (type(seq[i])==dict):
				continue
			o=None
			l=None
			for j in range(0,len(seq[i])):
				if (type(seq[i][j])==dict):
					continue
				if (j<2):
					if (type(seq[i][j][0][0])==dict):
						l=Compiler.eval_params(seq[i][j],VL=VL,FL=FL,CL=CL)[0]
					else:
						l=Variable("","bool",Compiler.eval_cond(seq[i][j],VL=VL,FL=FL,CL=CL))
				else:
					if (type(seq[i][j][0][0])==dict):
						r=Compiler.eval_params(seq[i][j],VL=VL,FL=FL,CL=CL)[0]
					else:
						r=Variable("","bool",Compiler.eval_cond(seq[i][j],VL=VL,FL=FL,CL=CL))
					v=None
					v1=l.value
					v2=r.value
					if (r.type!=l.type):
						v1=str(l.value)
						v2=str(r.value)
					if (seq[i][j-1]["t"]==Compiler.COND_EQ_CHAR):
						v=(v1==v2)
					if (seq[i][j-1]["t"]==Compiler.COND_NOT_EQ_CHAR):
						v=(v1!=v2)
					if (seq[i][j-1]["t"]==Compiler.COND_LESS_CHAR):
						v=(v1<v2)
					if (seq[i][j-1]["t"]==Compiler.COND_NOT_LESS_CHAR):
						v=(v1>=v2)
					if (seq[i][j-1]["t"]==Compiler.COND_MORE_CHAR):
						v=(v1>v2)
					if (seq[i][j-1]["t"]==Compiler.COND_NOT_MORE_CHAR):
						v=(v1<=v2)
					l=r
					if (o is None):
						o=v
					else:
						if (o==True and v==True):
							o=True
						else:
							o=False
			if (O is None):
				O=o
			else:
				if (seq[i-1]["t"]=="and"):
					if (O==True and o==True):
						O=True
					else:
						O=False
				if (seq[i-1]["t"]=="or"):
					if (O==True or o==True):
						O=True
					else:
						O=False
		return O
