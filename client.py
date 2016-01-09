#!/usr/bin/env python

import socket
import sys
import threading
import Queue
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import time

nickname = ""

class ReadThread (threading.Thread):
	def __init__(self, name, csoc, sendQueue, screenQueue):
		threading.Thread.__init__(self)
		self.name = name
		self.csoc = csoc
		self.nickname = ""
		self.sendQueue = sendQueue
		self.screenQueue = screenQueue
		
	def incoming_parser(self, data):

		if(data[0:3] == "TIC"):
			print "TIC"
			result = "TIC"

		elif(data[0:3] == "TOC"):
			result = "Connected to server"

		elif(data[0:3] == "HEL"):
			nickname = data[4:]
			result = "New nickname: " + str(nickname)

		elif(data[0:3] == "REJ"):
			result = "Nickname already exists."

		elif(data[0:3] == "BYE"):
			result = "CLS" #close socket signal
			return result

                elif(data[0:3] == "LSA"):
			result = "Users in the session: " + str(data[4:])

		elif(data[0:3] == "LUA"):
			result = "Sessions: " + str(data[4:])
                
                elif(data[0:3] == "JOK"):
			result = "JOK"
		
                elif(data[0:3] == "SOK"):
			print "Message sent to all users"
			result = "SOK"
		
		elif(data[0:3] == "SER"):
			result = "SER"
		
		elif(data[0:3] == "NEW"):
			result = "NEW"

		elif(data[0:3] == "NUM"):
			result = "NUM"
			
		elif(data[0:3] == "COK"):
                        result = "COK"

		elif(data[0:3] == "CER"):
			result = "CER"
			
		elif(data[0:3] == "TOK"):
			result = "TOK"
			
		elif(data[0:3] == "TER"):
			result = "TER"
			
		elif(data[0:3] == "END"):
			result = "END"
		
		elif(data[0:3] == "ERR"):
			result = "Incorrect command sent to server"

                elif(data[0:3] == "ERL"):
			result = "Please login with /nick command."

		else:
			result = data
		
		return result

	def run(self):
		while True: #for default client commands
			data = self.csoc.recv(1024)
			res = self.incoming_parser(data)
			print res
			if len(res) > 3 :
				if(res[0:3] == "CLS"): #close socket signal
					self.screenQueue.put("Thank you for connecting!")					
					self.csoc.close()
					quit()
					break
			if(res in ["TIC","MOK","SOK"]):
				continue
			self.screenQueue.put(res)			

class WriteThread (threading.Thread):
	def __init__(self, name, csoc, threadQueue):
		threading.Thread.__init__(self)
		self.name = name
		self.csoc = csoc
		self.threadQueue = threadQueue
		
	def run(self):
		while True:
			if not (self.threadQueue).empty():
				queue_message = self.threadQueue.get()
				try:
					self.csoc.send(queue_message)
				except socket.error:
					self.csoc.close()
					break


class ScreenThread(threading.Thread):
        def __init__(self, name, csoc, screenQueue, threadQueue):
		threading.Thread.__init__(self)
		self.name = name
		self.csoc = csoc
		self.screenQueue = screenQueue
		self.threadQueue = threadQueue

	def outgoing_parser(self, data):
		
		if len(data) == 0:
			return
		
		if data[0] == "/":
			cmdWithParam = data.split()
			command = cmdWithParam[0][1:]
			parameter = cmdWithParam[1]
			print command
			print str(parameter)
			if command == "list":
                                if parameter == "user" :
                                        self.screenQueue.put("LSQ")                                        
                                elif parameter == "session" :
                                        self.screenQueue.put("LUQ")
                                else:
                                        print "Command error. Try '/list session' or '/list user'."
				
			elif command == "quit":
				self.screenQueue.put("QUI")

			elif command == "nick":
				self.screenQueue.put("USR " + str(parameter[0]))

			elif command == "join":
				
				self.screenQueue.put("JOS")

			elif command == "new":
				self.screenQueue.put("NES")

			elif command == "next":
				self.screenQueue.put("NXT")

			elif command == "close":
				print close

			elif command == "cinko":
				self.screenQueue.put("CNK")

			elif command == "tombala":
				self.screenQueue.put("TOM")

			elif command == "help":
                                print "help"
				
			else:
				print "Command Error."

		else:
			print data
		

	def run(self):
		while True:
                        user_input = raw_input()
                        self.outgoing_parser(user_input)
                        

               
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
host = socket.gethostname()

port = 12345
s.connect((host, port))

socketQueue = Queue.Queue()
screenQueue = Queue.Queue()

rt = ReadThread("ReadThread", s, socketQueue, screenQueue)
rt.start()
wt = WriteThread("WriteThread", s, socketQueue)
wt.start()
st = ScreenThread("ScreenThread", s, socketQueue, screenQueue)
st.start()

rt.join()
wt.join()
st.join()

s.close()


