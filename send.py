# ~*~ coding: utf-8 ~*~
import socket
import hashlib
import simplejson as json

class sendInfo:
	def __init__(self, ip, port):
		self.address = (ip, int(port))

	def send(self, id, version, info):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			s.connect(self.address)
		except: return 1
		st = json.dumps(info)
		h = hashlib.md5()
		h.update(st)
#		print id, type(id)
		if(id == 'unknown'):
			id = socket.gethostbyaddr(socket.gethostname())[0]
		mes = 'Hello.\nID: ' + str(id.encode('utf-8')) + '\nVersion: ' + str(version) + '\nHash: ' + h.hexdigest() + '\n\n' + st
		self.sendParts(s, mes)
		try:		
			dat1 = s.recv(1024)
		except:
			return 1
		if(dat1[0:6] != 'Hello.'): 
			s.close()
			return 1
		if(dat1[7:15] == 'Update: '):
			link = dat1[14:]
			s.close()
			if(link != ''):
				self.deblink = link
				return 2
			else: return 1
		elif(dat1[7:] == 'Get info again.'):
			self.sendParts(s, mes)				
			dat2 = s.recv(1024)
			if(dat2 == 'Ok'):
				s.close()
				return 0
			else: 
				s.close()
				return 1
		elif(dat1[7:] == 'Ok'):
			s.close()
			return 0
		else:
			s.close()
			return 1

	def sendParts(self, s, st):
		lrang = len(range(0, len(st), 1024))-1
		for i in range(0, len(st), 1024):
			if(i < lrang):
				s.send(st[i:(1024+i)])
			else:
				s.send(st[i:])
				if(len(st[i:]) == 1024):
					s.send('END')	

	def getDeblink(self):
		return self.deblink

	def ready(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			s.connect(self.address)
		except: return 1
		s.send("Are you ready?")
		dat = s.recv(1024)
		if(dat == 'Yes.'): return 0
		else: return 1
