# ~*~ coding: utf-8 ~*~
#import xml.etree.ElementTree as etree
import lxml.etree
from lxml import etree
import time
import sys

class initXml:
	def __init__(self, xmlpath):
		self.path = xmlpath
		self.init = {'server': {}, 'check': {}}
		self.run = False

	def getInit(self):
		if(self.run == False): self.parse()
		return self.init

	def parse(self):
		self.tree = {}
		self.tree = lxml.etree.parse(self.path)
		for b in self.tree.getroot():
			if(b.tag == 'computer'):
					self.init['computer-id'] = b.attrib['id']
			elif(b.tag == 'check'):
				if(b.attrib['period'] == 'month'): self.init['check']['period'] = 777600000*int(b.attrib['every'])
				elif(b.attrib['period'] == 'week'): self.init['check']['period'] = 12960000*int(b.attrib['every'])
				elif(b.attrib['period'] == 'day'): self.init['check']['period'] = 216000*int(b.attrib['every'])
				elif(b.attrib['period'] == 'hour'): self.init['check']['period'] = 3600*int(b.attrib['every'])
				else: self.init['period'] = 12960000*int(b.attrib['check']['every'])
				self.init['check']['next'] = int(b[0].text)
			elif(b.tag == 'server'):
				for g in b:
					if(g.tag == 'ip'): 
						self.init['server']['ip'] = g.text
						self.init['server']['on-ip'] = True
					elif(g.tag == 'name'): 
						self.init['server']['name'] = g.text
						self.init['server']['on-ip'] = False
					elif(g.tag == 'port'): self.init['server']['port'] = g.text
		self.run = True

	def createInit(self, sett, version):
		sets = self.valid(self.parkeys(sett), create=True)
		if(sets == False): return 1

		nf = lxml.etree.Element('config')
		lxml.etree.SubElement(nf, 'product', attrib={'name': 'miron-client', 'version': version})
		lxml.etree.SubElement(nf, 'computer', attrib={'id': sets['id']})
		server = lxml.etree.SubElement(nf, 'server')
		ip = lxml.etree.SubElement(server, 'ip')
		ip.text = sets['ip']
		port = lxml.etree.SubElement(server, 'port')
		port.text = str(sets['port'])
		check = lxml.etree.SubElement(nf, 'check', attrib={'period': sets['check-period'], 'every': str(sets['check-every'])})
		next = lxml.etree.SubElement(check, 'next')
		next.text = str(sets['next-check'])

		f = open(self.path, 'w')
		f.write(lxml.etree.tounicode(nf, pretty_print=True))
		f.close()
		return 0

	def setInit(self, sett):
		sets = self.valid(self.parkeys(sett))
		if(sets == False): return 1
		if(self.run == False): self.parse()
		nf = self.tree
		for b in nf.getroot():
			if((b.tag == 'computer') and (sets.has_key('id') == 1)):
				b.attrib['id'] = sets['id'].decode("UTF8")
			elif(b.tag == 'server'):
				for b1 in b:
					if((b1.tag == 'ip') and (sets.has_key('ip') == 1)): b1.text = sets['ip']
					elif((b1.tag == 'port') and (sets.has_key('port') == 1)): b1.text = str(sets['port'])
			elif(b.tag == 'check'):
				if(sets.has_key('check-period') == 1):
					b.attrib['period'] = sets['check-period']
				if(sets.has_key('check-every') == 1):
					b.attrib['every'] = str(sets['check-every'])
				if(sets.has_key('next-check') == 1):
					for b2 in b:
						if(b2.tag == 'next'): b2.text = str(sets['next-check'])
		f = open(self.path, 'w')
		f.write(lxml.etree.tounicode(nf).encode('utf-8'))
		f.close()

	def valid(self, sets, create = False):
		if(sets.has_key('ip')):
			start = 0
			ip = ''
			for i in range(len(sets['ip'])):
				if(sets['ip'][i] == '.'):
					try: tek = int(sets['ip'][start:i])
					except: return False
					if(tek > 255) or (tek < 0): return False
					ip = ip + str(tek) + "."
					start = i+1
				elif((i+1) == len(sets['ip'])):
					try: tek = int(sets['ip'][start:])
					except: return False
					if(tek > 255) or (tek < 0): return False
					ip = ip + str(tek)
			sets['ip'] = ip
		if(sets.has_key('port')):
			try: port = int(sets['port'])
			except: return False
			if(port > 0): sets['port'] = port
			else: return False
		if(sets.has_key('next-check')):
			try: sets['next-check'] = int(sets['next-check'])
			except: sets['next-check'] = 0
		if(sets.has_key('check-every')):
			try: ce = int(sets['check-every'])
			except: return False
			if(ce > 0): sets['check-every'] = ce
			else: return False
		if(sets.has_key('check-period')):
			if((sets['check-period'] != 'hour') and (sets['check-period'] != 'day') and (sets['check-period'] != 'week') and (sets['check-period'] != 'month')):
				return False

		if((create == True) and (sets.has_key('ip') == 0)):
			return False
		if((create == True) and (sets.has_key('check-every') == 0)):
			sets['check-every'] = 2
		if((create == True) and (sets.has_key('check-period') == 0)):
			sets['check-period'] = 'week'
		if((create == True) and (sets.has_key('id') == 0)):
			sets['id'] = 'unknown'
		if((create == True) and (sets.has_key('port') == 0)):
			sets['port'] = 5015
		if((create == True) and (sets.has_key('next-check') == 0)):
			sets['next-check'] = 0

		return sets

	def parkeys(self, string):
		pars = {}
		startkey = -1
		startval = -1
		endval = ','
		for i in range(len(string)):
			if((startkey == -1) and ((string[i] == ' ') or (string[i] == '=') or (string[i] == '"') or (string[i] == "'") or (string[i] == ","))): pass
			elif(startkey == -1): startkey = i
			elif((startval == -1) and (string[i] == '=')):
				curkey = string[startkey:i]
				startval = i+1
				endval = ','
			elif(((string[i] == '"') or (string[i] == "'")) and (startval == i)):
				endval = string[i]
				startval = i+1
			elif(string[i] == endval):
				pars[curkey] = string[startval:i]
				startkey = -1
				startval = -1
				endval = ','
			elif((i+1) == len(string)):
				pars[curkey] = string[startval:]
		return pars

	def printConfig(self):
		if(self.run == False): self.parse()
		print "Продукт: miron-client " + str(MIRON_VERSION)
		print "Инвертарный номер: " + self.init['computer-id'].encode('utf-8')
		print "Обновления: 1 раз в " + str(self.init['check']['period']) + " секунд"
		if(self.init['check']['next'] < int(time.time())): print "Следующее обновление: при запуске"
		else: print "Следующее обновление: через " + str(int(time.time()) - self.init['check']['next']) + " секунд"
		print "Сервер: " + self.init['server']['ip'] + ":" + self.init['server']['port']

class lshwParse:
	def __init__(self, xmlpath):
		self.info  = {'matplat': {'developer': '', 'product': '', 'serial': ''}, 'cpu': [], 'memory': {'size': 0, 'slot': []}, 'video': [], 'usb': 0, 'hdd': [], 'cdrom': [], 'network': [], 'multimedia': []}
                self.path = xmlpath

	def run(self):
		tree = lxml.etree.parse(self.path, lxml.etree.XMLParser(recover=True))
		self.main(tree.getroot())
		return self.info

	def main(self, root):
		for ch in root:
			if((ch.tag == 'node') and (ch.attrib['id'][0:4] == 'core')):
				for ch1 in ch:
					if(ch1.tag == 'product'):
						self.info['matplat']['product'] = ch1.text
					elif(ch1.tag == 'vendor'):
						self.info['matplat']['developer'] = ch1.text
					elif(ch1.tag == 'serial'):
						self.info['matplat']['serial'] = ch1.text
					elif((ch1.tag == 'node') and (ch1.attrib['handle'] != '')):
						self.parse(ch1)	
		return 0

	def parse(self, curs):
		if(curs.attrib['class'] == 'bridge'):
			for ch in curs:
				if(ch.tag == 'node'): self.parse(ch)
		elif(curs.attrib['class'] == 'processor'):
			number_cpu = len(self.info['cpu'])
			self.info['cpu'].append({'product': '', 'developer': '', 'serial': '', 'mhz': ''})
			for ch2 in curs:
				if(ch2.tag == 'product'):
					self.info['cpu'][number_cpu]['product'] = ch2.text
				elif(ch2.tag == 'vendor'):
					self.info['cpu'][number_cpu]['developer'] = ch2.text
				elif(ch2.tag == 'serial'):
					self.info['cpu'][number_cpu]['serial'] = ch2.text
				elif(ch2.tag == 'size'):
					self.info['cpu'][number_cpu]['mhz'] = int(ch2.text)/1000000
		elif((curs.attrib['id'][0:6] == 'memory')):
			for ch3 in curs:
				if(ch3.tag == 'size'):
					self.info['memory']['size'] = int(ch3.text)/1024/1024
				if((curs.tag == 'node') and (curs.attrib['class'] == 'memory')):
					b = {'about': '', 'size': 0}
					for ch4 in ch3:
						if(ch4.tag == 'description'):
							b['about'] = ch4.text
						elif(ch4.tag == 'size'):
							b['size'] = int(ch4.text)/1024/1024
					if(b['size'] > 0): 
						self.info['memory']['slot'].append(b)
		elif((curs.attrib['id'][0:7] == 'display') and (curs.attrib['class'] == 'display')):
			number_video = len(self.info['video'])
			self.info['video'].append({'product': '', 'developer': ''})
			for ch in curs:
				if(ch.tag == 'product'):
					self.info['video'][number_video]['product'] = ch.text
				elif(ch.tag == 'vendor'):
					self.info['video'][number_video]['developer'] = ch.text
		elif(curs.attrib['class'] == 'bus'):
			if(curs.attrib['id'][0:3] == 'usb'):
				self.info['usb'] = self.info['usb'] + 1
		elif(curs.attrib['class'] == 'storage'):
			for ch in curs:
				if(ch.tag == 'businfo'): 
					if(ch.text[0:3] == 'usb'): return 0
					else: self.disk(curs)
		elif((curs.attrib['id'][0:7] == 'network') and (curs.attrib['class'] == 'network')):
			number_network = len(self.info['network'])
			self.info['network'].append({'product': '', 'developer': '', 'speed': 0, 'serial': ''})
			for ch in curs:
				if(ch.tag == 'product'):
					self.info['network'][number_network]['product'] = ch.text
				elif(ch.tag == 'vendor'):
					self.info['network'][number_network]['developer'] = ch.text
				elif(ch.tag == 'capacity'):
					self.info['network'][number_network]['speed'] = int(ch.text)/1000000
				elif(ch.tag == 'serial'):
					self.info['network'][number_network]['serial'] = ch.text
		elif((curs.attrib['id'][0:10] == 'multimedia') and (curs.attrib['class'] == 'multimedia')):
			number_multimedia = len(self.info['multimedia'])
			self.info['multimedia'].append({'product': '', 'developer': ''})
			for ch in curs:
				if(ch.tag == 'product'):
					self.info['multimedia'][number_multimedia]['product'] = ch.text
				elif(ch.tag == 'vendor'):
					self.info['multimedia'][number_multimedia]['developer'] = ch.text
		return 0

	def disk(self, curs):
		for ch in curs:
			if(ch.tag == 'node'):
				if(ch.attrib['id'][0:4] == 'disk'):
					number_hdd = len(self.info['hdd'])
					self.info['hdd'].append({'product': '', 'developer': '', 'serial': '', 'signature': '', 'size': 0})
					for ch1 in ch:
						if(ch1.tag == 'product'):
							self.info['hdd'][number_hdd]['product'] = ch1.text
						elif(ch1.tag == 'vendor'):
							self.info['hdd'][number_hdd]['developer'] = ch1.text
						elif(ch1.tag == 'serial'):
							self.info['hdd'][number_hdd]['serial'] = ch1.text
						elif(ch1.tag == 'size'):
							self.info['hdd'][number_hdd]['size'] = int(ch1.text)/1024/1024/1024
						elif(ch1.tag == 'configuration'):
							for ch2 in ch1:
								if(ch2.attrib['id'] == 'signature'):
									self.info['hdd'][number_hdd]['signature'] = ch2.attrib['value']
				elif(ch.attrib['id'][0:5] == 'cdrom'):
					number_cdrom = len(self.info['cdrom'])
					self.info['cdrom'].append({'product': '', 'developer': '', 'serial': ''})
					for ch1 in ch:
						if(ch1.tag == 'product'):
							self.info['cdrom'][number_cdrom]['product'] = ch1.text
						elif(ch1.tag == 'vendor'):
							self.info['cdrom'][number_cdrom]['developer'] = ch1.text
						elif(ch1.tag == 'serial'):
							self.info['cdrom'][number_cdrom]['serial'] = ch1.text
		return 0

	def see(self):
		print "МАТЕРИНСКАЯ ПЛАТА"
		print "  Производитель: " + self.info['matplat']['developer']
		print "  Модель: " + self.info['matplat']['product']
		print "  Серийный номер: " + self.info['matplat']['serial']


		if(len(self.info['cpu']) == 1): print "ПРОЦЕССОР"
		else: print "ПРОЦЕССОРЫ"
		for t in self.info['cpu']:
			print "  Производитель: " + t['developer']
			print "  Модель: " + t['product']
			print "  Частота: " + str(t['mhz']) + 'MHz'
			print "  Серийный номер: " + t['serial']


		print "ОПЕРАТИВНАЯ ПАМЯТЬ"
		print "  Общий объём: " + str(self.info['memory']['size']) + "MB"
		print "  Плашки:"
		i = 1
		for t in self.info['memory']['slot']:
			print "    " + str(i) + ")",
			print "Наименование: " + t['about']
			print "       Размер: " + str(t['size']) + "MB"
			i = i + 1


		print "ВИДЕОКАРТА"
		if(len(self.info['video']) == 1):
			print "  Производитель: " + self.info['video'][0]['developer']
			print "  Модель: " + self.info['video'][0]['product']
		else:
			for t in range(len(self.info['video'])):
				print "  Производитель: " + self.info['video'][t]['developer']
				print "  Модель: " + self.info['video'][t]['product']


		print "ЖЁСТКИЙ ДИСК"
		if(len(self.info['hdd']) == 1):
			print "  Производитель: " + self.info['hdd'][0]['developer']
			print "  Модель: " + self.info['hdd'][0]['product']
			print "  Размер: " + str(self.info['hdd'][0]['size']) + "GB"
			print "  Серийный номер: " + self.info['hdd'][0]['serial']
			print "  Сигнатура: " + self.info['hdd'][0]['signature']
		else:
			for t in range(len(self.info['hdd'])):
				print "    " + str(t+1) + ")",
				print "Производитель: " + self.info['hdd'][t]['developer']
				print "       Модель: " + self.info['hdd'][t]['product']
				print "       Размер: " + str(self.info['hdd'][t]['size']) + "GB"
				print "       Серийный номер: " + self.info['hdd'][t]['serial']
				print "       Сигнатура: " + self.info['hdd'][t]['signature']


		print "ОПТИЧЕСКИЕ ПРИВОДЫ"
		if(len(self.info['cdrom']) == 1):
			print "  Производитель: " + self.info['cdrom'][0]['developer']
			print "  Модель: " + self.info['cdrom'][0]['product']
			print "  Серийный номер: " + self.info['cdrom'][0]['serial']
		else:
			for t in range(len(self.info['cdrom'])):
				print "    " + str(t+1) + ")",
				print "Производитель: " + self.info['cdrom'][t]['developer']
				print "       Модель: " + self.info['cdrom'][t]['product']
				print "       Серийный номер: " + self.info['cdrom'][t]['serial']


		print "СЕТЕВЫЕ ПЛАТЫ"
		if(len(self.info['network']) == 1):
			print "  Производитель: " + self.info['network'][0]['developer']
			print "  Модель: " + self.info['network'][0]['product']
			print "  Скорость: " + str(self.info['network'][0]['speed']) + "MB/s"
			print "  Серийный номер: " + self.info['network'][0]['serial']
		else:
			for t in range(len(self.info['network'])):
				print "    " + str(t+1) + ")",
				print "Производитель: " + self.info['network'][t]['developer']
				print "       Модель: " + self.info['network'][t]['product']
				print "       Скорость: " + str(self.info['network'][t]['speed']) + "MB/s"
				print "       Серийный номер: " + self.info['network'][t]['serial']


		print "МУЛЬТИМЕДИА УСТРОЙСТВА"
		if(len(self.info['multimedia']) == 1):
			print "  Производитель: " + self.info['multimedia'][0]['developer']
			print "  Модель: " + self.info['multimedia'][0]['product']
		else:
			for t in range(len(self.info['multimedia'])):
				print "    " + str(t+1) + ")",
				print "Производитель: " + self.info['multimedia'][t]['developer']
				print "       Модель: " + self.info['multimedia'][t]['product']


		print "USB портов: " + str(self.info['usb'])
