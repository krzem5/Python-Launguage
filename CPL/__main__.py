from .compiler import Compiler
import colorama
import ctypes
import glob
import os
import sys



colorama.init()



def write(t):
	print("\033[22;37m"+t,end="")
def write_warn(w):
	print("\033[2;33m"+w,end="")
def write_error(e):
	print("\033[2;31m"+e,end="")



if ("--compile" in sys.argv):
	sys.argv=sys.argv[1:]
	D=("--debug" in sys.argv)
	pl=[]
	for a in sys.argv:
		if (a[0]!="-"):
			pl+=[a]
	if (len(pl)==0):
		pl=glob.glob("*.cpl")
	for p in pl:
		p=os.path.abspath(os.path.join(os.getcwd(),p))
		if (not os.path.isfile(p)):
			continue
		ctypes.windll.kernel32.SetConsoleTitleW("Compiling \u2012 "+os.path.abspath(p))
		op=os.path.abspath(p).rsplit(".",1)[0]+".ccpl"
		with open(p,"r") as f:
			e=Compiler.compile(f.read(),S=[os.path.abspath(p)],D=D)
			if (hasattr(e,"ERROR") and e.ERROR==True):
				write_error(e.print())
			else:
				with open(op,"wb") as f:
					f.write(e)
elif ("--run" in sys.argv):
	sys.argv=sys.argv[1:]
	p=None
	for a in sys.argv:
		if (a[0]!="-"):
			p=a+".ccpl"
	if (p==None):
		p=glob.glob(os.path.join(os.getcwd(),"*.ccpl"))[0]
	p=os.path.abspath(os.path.join(os.getcwd(),p))
	ctypes.windll.kernel32.SetConsoleTitleW("Running \u2012 "+os.path.abspath(p))
	with open(os.path.abspath(p),"rb") as f:
		Compiler.run(f.read())
else:
	write(f"cpl v{Compiler.RE_VERSION}\n")
	write(f"cplc v{Compiler.C_VERSION}")