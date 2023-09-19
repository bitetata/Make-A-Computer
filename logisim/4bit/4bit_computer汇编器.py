# _*_ coding: utf-8 _*_
import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import tkinter.filedialog as filedialog
import fileinput
import re
import sys

romAddrBits = 4		#ROM地址的位数
romDataBits = 4		#ROM数据的位数
romAddrMask = pow(2, romAddrBits) - 1		#转换成mask。比如romAddrBits=8，那么romAddrMask=二进制的11111111
romDataMask = pow(2, romDataBits) - 1		#转换成mask。比如romDataBits=4，那么romDataMask=二进制的1111

def genOneCode(addr=0, data=0, enData=0, enLedIn=0, enAddOut=0, enAddIn1=0, enAddIn2=0, enMemOut=0, enMemAddrIn=0, enMemDataIn=0, enCmpIn2=0, enCmpIn1=0, enCmpOut=0, enKeyIn=0):
	"""
	addr：ROM地址（0-3 bit）
	data：ROM数据（4-7 bit）
	enData：控制“ROM数据”是否链接总线（8 bit）
	enLedIn：控制“LED输入”是否链接总线（9 bit）
	enAddOut：控制“加法器输出”是否链接总线（10 bit）
	enAddIn1：控制“加法器输入1”是否链接总线（11 bit）
	enAddIn2：控制“加法器输入2”是否链接总线（12 bit）
	enMemOut：控制“内存输出”是否链接总线（13 bit）
	enMemAddrIn：控制“内存地址输入”是否链接总线（14 bit）
	enMemDataIn：控制“内存数据输入”是否链接总线（15 bit）
	enCmpIn2：控制“比较器输入2”是否链接总线（16 bit）
	enCmpIn1：控制“比较器输入1”是否链接总线（17 bit）
	enCmpOut：控制“比较器输出”是否链接总线（18 bit）
	enKeyIn：控制“按键输入”是否链接总线（19 bit）
	"""
	otherBits = romAddrBits + romDataBits
	d1 = addr & romAddrMask
	d2 = (data & romDataMask) << romAddrBits
	d3 = enData << (otherBits + 0)
	d4 = enLedIn << (otherBits + 1)
	d5 = enAddOut << (otherBits + 2)
	d6 = enAddIn1 << (otherBits + 3)
	d7 = enAddIn2 << (otherBits + 4)
	d8 = enMemOut << (otherBits + 5)
	d9 = enMemAddrIn << (otherBits + 6)
	d10 = enMemDataIn << (otherBits + 7)
	d11 = enCmpIn2 << (otherBits + 8)
	d12 = enCmpIn1 << (otherBits + 9)
	d13 = enCmpOut << (otherBits + 10)
	d14 = enKeyIn << (otherBits + 11)
	return (d1|d2|d3|d4|d5|d6|d7|d8|d9|d10|d11|d12|d13|d14)

def genMoveCode(arg1, arg2, startAddr):
	"""
	地址0：把“内存地址arg1”传送到总线
	地址1：把总线数据传送给内存的地址输入端
	地址2：把“数字arg2”传送到总线
	地址3：把总线数据传送给内存的数据输入端完成保存
	例子：MOV [0], 1
	"""
	print("move", arg1, arg2, startAddr)
	return [
		genOneCode(addr=startAddr+1, data=arg1, enData=1),
		genOneCode(addr=startAddr+2, data=arg1, enData=1, enMemAddrIn=1),
		genOneCode(addr=startAddr+3, data=arg2, enData=1),
		genOneCode(addr=startAddr+4, data=arg2, enData=1, enMemDataIn=1),
	]

def genAddCode(arg1, arg2, arg3, startAddr):
	"""
	地址0：把数据“内存地址arg2”传送到总线
    地址1：把总线数据传送给内存的地址输入端
    地址2：把内存数据传输到总线上
    地址3：总线数据被保存到加法器的寄存器1里
    地址4：把数据“内存地址arg3”传送到总线
    地址5：把总线数据传送给内存的地址输入端
    地址6：把内存数据传输到总线上
    地址7：总线数据被保存到加法器的寄存器2里
    地址8：把数据“内存地址arg1”传送到总线
    地址9：把总线数据传送给内存的地址输入端
    地址10：使加法器输出的计算的结果传送到总线
    地址11：把总线数据传送给内存的数据输入端完成保存
    例子：ADD [2], [1], [0]
	"""
	print("add", arg1, arg2, arg3, startAddr)
	return [
		genOneCode(addr=startAddr+1, data=arg2, enData=1),
		genOneCode(addr=startAddr+2, data=arg2, enData=1, enMemAddrIn=1),
		genOneCode(addr=startAddr+3, enMemOut=1),
		genOneCode(addr=startAddr+4, enMemOut=1, enAddIn1=1),
		genOneCode(addr=startAddr+5, data=arg3, enData=1),
		genOneCode(addr=startAddr+6, data=arg3, enData=1, enMemAddrIn=1),
		genOneCode(addr=startAddr+7, enMemOut=1),
		genOneCode(addr=startAddr+8, enMemOut=1, enAddIn1=2),
		genOneCode(addr=startAddr+9, data=arg1, enData=1),
		genOneCode(addr=startAddr+10, data=arg1, enData=1, enMemAddrIn=1),
		genOneCode(addr=startAddr+11, enAddOut=1),
		genOneCode(addr=startAddr+12, enAddOut=1, enMemDataIn=1),
	]

def genAdd2Code(arg1, arg2, arg3, startAddr):
	"""
	地址0：把数据“内存地址arg2”传送到总线
    地址1：把总线数据传送给内存的地址输入端
    地址2：把内存数据传输到总线上
    地址3：总线数据被保存到加法器的寄存器1里
    地址4：把数据“内存地址arg3”传送到总线
    地址5：把总线数据传送给内存的地址输入端
    地址6：把内存数据传输到总线上
    地址7：总线数据被保存到加法器的寄存器2里
    地址8：把数据“内存地址arg1”传送到总线
    地址9：把总线数据传送给内存的地址输入端
    地址10：把内存数据传输到总线上
    地址11：把总线数据传送给内存的地址输入端
    地址12：使加法器输出的计算的结果传送到总线
    地址13：把总线数据传送给内存的数据输入端完成保存
    例子：ADD [[2]], [1], [0]
	"""
	print("add", arg1, arg2, arg3, startAddr)
	return [
		genOneCode(addr=startAddr+1, data=arg2, enData=1),
		genOneCode(addr=startAddr+2, data=arg2, enData=1, enMemAddrIn=1),
		genOneCode(addr=startAddr+3, enMemOut=1),
		genOneCode(addr=startAddr+4, enMemOut=1, enAddIn1=1),
		genOneCode(addr=startAddr+5, data=arg3, enData=1),
		genOneCode(addr=startAddr+6, data=arg3, enData=1, enMemAddrIn=1),
		genOneCode(addr=startAddr+7, enMemOut=1),
		genOneCode(addr=startAddr+8, enMemOut=1, enAddIn1=2),
		genOneCode(addr=startAddr+9, data=arg1, enData=1),
		genOneCode(addr=startAddr+10, data=arg1, enData=1, enMemAddrIn=1),
		genOneCode(addr=startAddr+11, enMemOut=1),
		genOneCode(addr=startAddr+12, enMemOut=1, enMemAddrIn=1),
		genOneCode(addr=startAddr+13, enAddOut=1),
		genOneCode(addr=startAddr+14, enAddOut=1, enMemDataIn=1),
	]

def genJumpCode(arg1, startAddr):
	"""
	直接把“指令地址arg1”设置到ROM的地址位里
	例子：JUMP ADDR
	"""
	print("jump", arg1, startAddr)
	return [
		arg1,
	]

def genJumpIfCode(arg1, arg2, arg3, startAddr):
	"""
	地址0：把数据“内存地址arg2”传送到总线
    地址1：把总线数据传送给内存的地址输入端
    地址2：把内存数据传输到总线上
    地址3：总线数据被保存到比较器的寄存器1里
    地址4：把数据“内存地址arg3”传送到总线
    地址5：把总线数据传送给内存的地址输入端
    地址6：把内存数据传输到总线上
    地址7：总线数据被传送到比较器的寄存器2里
    地址8：使比较器的输出结果生效
    地址9：本条指令的地址位被设置成“当前地址+2”，即下下条指令地址
    地址10：本条指令的地址位被设置成“目标指令地址arg1”
    例子：JUMPIF ADDR, [0], [1]
	"""
	print("jumpif", arg1, arg2, arg3, startAddr)
	return [
		genOneCode(addr=startAddr+1, data=arg2, enData=1),
		genOneCode(addr=startAddr+2, data=arg2, enData=1, enMemAddrIn=1),
		genOneCode(addr=startAddr+3, enMemOut=1),
		genOneCode(addr=startAddr+4, enMemOut=1, enCmpIn1=1),
		genOneCode(addr=startAddr+5, data=arg3, enData=1),
		genOneCode(addr=startAddr+6, data=arg3, enData=1, enMemAddrIn=1),
		genOneCode(addr=startAddr+7, enMemOut=1),
		genOneCode(addr=startAddr+8, enMemOut=1, enCmpIn2=1),
		genOneCode(addr=startAddr+9, enCmpOut=1),
		genOneCode(addr=startAddr+11),
		arg1,
	]

def genOutCode(arg1, startAddr):
	"""
	地址1：把“内存地址arg1”传送到总线
	地址2：把总线数据传送给内存的地址输入端
	地址3：把内存数据传输到总线上
	地址4：把总线数据传送给“十六进制数码管”显示出来
	例子：OUT [0]
	"""
	print("out", arg1, startAddr)
	return [
		genOneCode(addr=startAddr+1, data=arg1, enData=1),
		genOneCode(addr=startAddr+2, data=arg1, enData=1, enMemAddrIn=1),
		genOneCode(addr=startAddr+3, enMemOut=1),
		genOneCode(addr=startAddr+4, enMemOut=1, enLedIn=1),
	]

def genInCode(arg1, startAddr):
	"""
	地址1：把数据“内存地址arg1”传送到总线
	地址2：把总线数据传送给内存的地址输入端
	地址3：使“按钮”的数据传送到总线
	地址4：把总线数据传送给内存的数据输入端完成保存
	例子：IN [0]
	"""
	print("in", arg1, startAddr)
	return [
		genOneCode(addr=startAddr+1, data=arg1, enData=1),
		genOneCode(addr=startAddr+2, data=arg1, enData=1, enMemAddrIn=1),
		genOneCode(addr=startAddr+3, enKeyIn=1),
		genOneCode(addr=startAddr+4, enKeyIn=1, enMemDataIn=1),
	]

#compile
def compileOneLine(text, startAddr):
	m = re.match(r'^[ \t]*mov[ \t]+\[(\d+)\][ \t]*,[ \t]*(\d+)[ \t]*$', text)
	if m:
		arg1 = int(m.groups()[0])
		arg2 = int(m.groups()[1])
		return genMoveCode(arg1, arg2, startAddr)
	m = re.match(r'^[ \t]*add[ \t]+\[(\d+)\][ \t]*,[ \t]*\[(\d+)\][ \t]*,[ \t]*\[(\d+)\][ \t]*$', text)
	if m:
		arg1 = int(m.groups()[0])
		arg2 = int(m.groups()[1])
		arg3 = int(m.groups()[2])
		return genAddCode(arg1, arg2, arg3, startAddr)
	m = re.match(r'^[ \t]*add[ \t]+\[\[(\d+)\]\][ \t]*,[ \t]*\[(\d+)\][ \t]*,[ \t]*\[(\d+)\][ \t]*$', text)
	if m:
		arg1 = int(m.groups()[0])
		arg2 = int(m.groups()[1])
		arg3 = int(m.groups()[2])
		return genAdd2Code(arg1, arg2, arg3, startAddr)
	m = re.match(r'^[ \t]*jump[ \t]+(\w+)[ \t]*$', text)
	if m:
		arg1 = m.groups()[0]
		return genJumpCode(arg1, startAddr)
	m = re.match(r'^[ \t]*jumpif[ \t]+(\w+)[ \t]*,[ \t]*\[(\d+)\][ \t]*,[ \t]*\[(\d+)\][ \t]*$', text)
	if m:
		arg1 = m.groups()[0]
		arg2 = int(m.groups()[1])
		arg3 = int(m.groups()[2])
		return genJumpIfCode(arg1, arg2, arg3, startAddr)
	m = re.match(r'^[ \t]*out[ \t]+\[(\d+)\][ \t]*$', text)
	if m:
		arg1 = int(m.groups()[0])
		return genOutCode(arg1, startAddr)
	m = re.match(r'^[ \t]*in[ \t]+\[(\d+)\][ \t]*$', text)
	if m:
		arg1 = int(m.groups()[0])
		return genInCode(arg1, startAddr)


def complieCode(text):
	labelAddrMap = {}
	binCodeList = []
	lineNumber = 0
	for line in text.split("\n"):
		lineNumber = lineNumber + 1
		line = line.split("//")[0].strip().lower()
		if len(line) <= 0:
			continue
		m = re.match(r'^[ \t]*(\w+):[ \t]*$', line)
		if m:
			arg1 = m.groups()[0]
			labelAddrMap[arg1] = len(binCodeList)
		else:
			oneCodes = compileOneLine(line, len(binCodeList))
			if oneCodes != None:
				binCodeList.extend(oneCodes)
			else:
				tk.messagebox.showinfo('语法错误', "Line " + str(lineNumber) + ":\n" + line)
				return
	#把label修正成ROM地址
	print(labelAddrMap)
	for i in range(0,len(binCodeList)):
		if not isinstance(binCodeList[i], int):
			if binCodeList[i] in labelAddrMap:
				binCodeList[i] = labelAddrMap[binCodeList[i]] & romAddrMask
			else:
				tk.messagebox.showinfo('语法错误', "Unknown label:\n" + binCodeList[i])
				return
	print(binCodeList)
	return binCodeList


#
#以下是所有UI界面代码
#
class editor:
	def __init__(self,rt):
		if rt==None:
			self.t=tk.Tk()
		else:
			self.t=tk.Toplevel(rt)
		self.t.title("汇编器")
		self.t.geometry("550x600")
		self.bar=tk.Menu(rt)

		self.filem=tk.Menu(self.bar, tearoff=0)
		self.filem.add_command(label="打开",command=self.openfile)
		self.filem.add_command(label="保存",command=self.savefile)
		self.filem.add_separator()
		self.filem.add_command(label="退出",command=self.die)

		self.compilem=tk.Menu(self.bar, tearoff=0)
		self.compilem.add_command(label="编译生成Bin文件",command=self.compile)

		self.bar.add_cascade(label="文件",menu=self.filem)
		self.bar.add_cascade(label="编译",menu=self.compilem)
		self.t.config(menu=self.bar)

		self.f=tk.Frame(self.t,width=512)
		self.f.pack(expand=1,fill=tk.BOTH)

		self.st=scrolledtext.ScrolledText(self.f,background="white", font=('courier', 20, 'normal'))
		self.st.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)

	def close(self):
		self.t.destroy()

	def die(self):
		sys.exit(0)

	def openfile(self):
		p1=tk.END
		oname=filedialog.askopenfilename(filetypes=[("Python file","*.txt")])
		if oname:
			self.st.delete('1.0', tk.END)
			for line in fileinput.input(oname, encoding="utf-8"):
				self.st.insert(p1,line)
			self.t.title(oname)

	def savefile(self):
		self.savefileData(self.st.get(1.0,tk.END))

	def savefileData(self, data):
		sname=filedialog.asksaveasfilename(filetypes=[("Python file","*.txt")])
		if sname:
			ofp=open(sname,"w")
			ofp.write(data)
			ofp.flush()
			ofp.close()
			self.t.title(sname)

	def compile(self):
		binCodeList = complieCode(self.st.get(1.0,tk.END))
		if binCodeList != None:
			dataList = ["v2.0 raw"]
			lineCount = (len(binCodeList)+15) // 16
			for x in range(0,lineCount):
				lineDataList = []
				for y in range(16*x, 16*(x+1)):
					if y >= len(binCodeList):
						break
					lineDataList.append("%X" % binCodeList[y])
				dataList.append(' '.join(lineDataList))
			data = '\n'.join(dataList)
			self.savefileData(data)


if __name__=="__main__":
	editor(None).t.mainloop()
