# ~*~ coding: utf-8 ~*~
from datetime import date

class logWrite:

	def __init__(self, fpath, write=True):
		self.real_write = write
		if(self.real_write == True):
			# открытие файла лога для записи
			self.f = open(fpath, 'a')

	def write(self, msg, quit = False):
		print msg
		if(self.real_write == True):
			# запись в файл лога сообщение: 'Текущее время: msg'
			# если end равно True, то закрытие лога - вызов функции end
			self.f.write(str(date.today()) + ": " + msg + '\n')
		if(quit == True): 
			self.end()

	def end(self):
		if(self.real_write == True):
			# закрытие лога
			self.f.close()


def init_log(path, use_log):
	if(use_log == False):
		log = logWrite("", False)
	else:
		try:
			log = logWrite(path)
		except IOError, exc:
			print "\nОшибка: " + str(exc)
			print "Возможно вы запускаете программу без прав администратора!\n"
			exit()
	return log
