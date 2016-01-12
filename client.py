#!/usr/bin/env python

import socket
import sys
import threading
import Queue
import time
from collections import OrderedDict
import re
import ast

nickname = ""
card = OrderedDict()
cinko_count = 0
past_num_list = []

class ReadThread (threading.Thread):
	def __init__(self, name, csoc, socketQueue, screenQueue):
		threading.Thread.__init__(self)
		self.name = name
		self.csoc = csoc
		self.nickname = ""
		self.socketQueue = socketQueue
		self.screenQueue = screenQueue
		
	def incoming_parser(self, data):
                result = ''
                parameter = ''
                parameter2 = ''
                cmdWithParam = data.split()
		command = cmdWithParam[0][1:]
		if len(cmdWithParam) == 2:
                        parameter = cmdWithParam[1]
                if len(cmdWithParam) == 3:
                        
                        parameter = cmdWithParam[1]
                        parameter2 = cmdWithParam[2]
                        
		if(data[0:3] == "TIC"):
			socketQueue.put("TOC")

		elif(data[0:3] == "TOC"):
			result = "Connected to server"

		elif(data[0:3] == "HEL"):
			print "Your nickname: " +  str(parameter)
			
		elif(data[0:3] == "REJ"):
			print "Nickname already exists."

		elif(data[0:3] == "BYE"):
			result = "BYE" #close socket signal
			
                elif(data[0:3] == "LSA"):
                        if(parameter == ''):
                                print "No session found"
                        else:
                                print "Sessions: " +  str(parameter)

		elif(data[0:3] == "LUA"):
                        if(parameter == ''):
                                print "No user in the session"
                        else:
                                print "Users in the session: " +  str(parameter)

		elif(data[0:3] == "LNA"):
			print "You cannot list users before you login a session."
                
                elif(data[0:3] == "JOK"):
                        print "Waiting for other users to login..."
			socketQueue.put("RDY")

		elif(data[0:3] == "FUL"):
                        print "Session is full. Join/create another session."
					
                elif(data[0:3] == "SOK"):
                        print "Waiting for other users to login..."
			socketQueue.put("RDY")
		
		elif(data[0:3] == "SER"):
			print "Session name already exists."
		
		elif(data[0:3] == "NEW"):
                        number_list = (str(data[5:-1])).split(", ")
                        for i in range(len(number_list)):
                                card[number_list[i]] = ' '
                        print "Game has started."
                        printCard()
                        
		elif(data[0:3] == "NUM"):
                        past_num_list.append(parameter)
                        print "Next number is: " + str(parameter)
                        printCard()
                        
						
		elif(data[0:3] == "COK"):
                        cinko_list = parameter2.split(":")
                        size = len(cinko_list)
                        if size == 1:
                                result = "1st"
                        elif size == 2:
                                result = "2nd"
                        elif size == 3:
                                result = "3rd"  

                        print result + " Cinko. User: " + parameter
                                                
		elif(data[0:3] == "CER"):
                        print "Wrong Cinko. You must close all numbers in a row."
						
		elif(data[0:3] == "TOK"):
                        print "TOMBALA. Game over. Winner: " + parameter
						
		elif(data[0:3] == "TER"):
                        print "Wrong Tombala. You must close all numbers."
						
		elif(data[0:3] == "END"):
			print "END"
		
		elif(data[0:3] == "ERR"):
			print "Incorrect command for server"

                elif(data[0:3] == "ERL"):
			print "Please login with /nick command."

		else:
			return
		
		return result

	def run(self):
		while True: #for default client commands
                        res = ''
			data = self.csoc.recv(1024)
			res = self.incoming_parser(data)
                        if res == '':
                                continue
                        if len(res) > 3 :
				if(res[0:3] == "BYE"): #close socket signal
					print "Thank you for connecting!"
					self.csoc.close()
					break
				

class WriteThread (threading.Thread):
	def __init__(self, name, csoc, socketQueue):
		threading.Thread.__init__(self)
		self.name = name
		self.csoc = csoc
		self.socketQueue = socketQueue
		
	def run(self):
		while True:
			if not (self.socketQueue).empty():
				queue_message = self.socketQueue.get()
				try:
                                       self.csoc.send(queue_message)
				except socket.error:
					self.csoc.close()
					break


class ScreenThread(threading.Thread):
        def __init__(self, name, csoc, screenQueue, socketQueue):
		threading.Thread.__init__(self)
		self.name = name
		self.csoc = csoc
		self.screenQueue = screenQueue
		self.socketQueue = socketQueue

	def outgoing_parser(self, data):
		
		if len(data) == 0:
			return
		
		if data[0] == "/":
			cmdWithParam = data.split()
			command = cmdWithParam[0][1:]
			if len(cmdWithParam) == 2:
                                parameter = cmdWithParam[1]
                        elif len(cmdWithParam ) > 2:
                                print "Command error. There should be only 1 space in the command. Example: '/nick JohnSmith' but not '/nick John Smith'."
                                return
			
			if command == "list":
                                if len(cmdWithParam) == 2:                                        
                                        if parameter == "user" :
                                                self.screenQueue.put("LUQ")                                        
                                        elif parameter == "session" :
                                                self.screenQueue.put("LSQ")
                                        else:
                                                print "Command error. Try '/list session' or '/list user'."
                                                return
                                else:
                                        print "Command error. Try '/list session' or '/list user'."
                                        return
				
			elif command == "quit":
				self.screenQueue.put("QUI")

			elif command == "nick":
                                if len(cmdWithParam) == 2:
                                        self.screenQueue.put("USR " + parameter)
                                else:
                                        print "Command error. Try '/nick {nick name}'. Example: /nick John"
                                        return
                                
			elif command == "join":
				if len(cmdWithParam) == 2:                                        
                                        self.screenQueue.put("JOS " + parameter)
                                else:
                                        print "Command error. Try '/join {session name}'. Example: /join Pros"
                                        return

			elif command == "new":
				if len(cmdWithParam) == 2:                                        
                                        self.screenQueue.put("NES " + parameter)
                                else:
                                        print "Command error. Try '/new {session name}'. Example: /new Pros"
                                        return

			elif command == "next":
                                print "Waiting for other users..."
				self.screenQueue.put("NXT")

			elif command == "close":
                                if len(cmdWithParam) == 2:
                                        

                                        if parameter not in past_num_list:
                                             print "You can only close " + ','.join(past_num_list)
                                        
                                        if parameter not in card:
                                                print "Number " + parameter + " is not in your card."
                                                
                                        if parameter in card:
                                        
                                                card[parameter] = '* '
                                          
                                else:
                                        print "Command error. Try '/close {number}'. Example: '/close 26'."
                                
				printCard()

			elif command == "cinko":
                                print "CNK " + str(card)
				self.screenQueue.put("CNK " + str(card))

			elif command == "tombala":
				self.screenQueue.put("TOM " + str(card))

			elif command == "help":
                                f = open("help.txt", 'r')
                                for line in f:
                                        print line
				
			else:
				print "Command Error. Please type /help for commands."

		else:
                        print "Command error. Please type /help for commands."
					

	def run(self):
		while True:
                        user_input = raw_input()
                        self.outgoing_parser(user_input)
def printCard():
        out = '\nYour card is: \n'
        for i in range(15):
                out +=  (str(card.items()[i][0]) + card.items()[i][1])
                if(i%5 == 4 ):
                        out += '\n'
        print out
                        

print "\nWelcome aboard! The list of commands given below: \n"
f = open("help.txt", 'r')
for line in f:
        print line
             
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



