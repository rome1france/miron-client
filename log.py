# ~*~ coding: utf-8 ~*~
from datetime import date

class logWrite:

	def __init__(self, fpath, emulation=False):
		self.emulation = emulation
		if(self.emulation == False):
			# открытие файла лога для записи
			self.f = open(fpath, 'a')

	def write(self, msg, end = False):
		if(self.emulation == False):
			# запись в файл лога сообщение: 'Текущее время: msg'
			# если end равно True, то закрытие лога - вызов функции end
			self.f.write(str(date.today()) + ": " + msg + '\n')
		if(end == True): 
			self.end()

	def end(self):
		if(self.emulation == False):
			# закрытие лога
			self.f.close()
