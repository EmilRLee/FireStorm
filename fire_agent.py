#!/usr/bin/python3.6

import socket, sys, struct, os, time

HOST = '192.168.5.24'
PORT = 5050

class fireagent:


	def getHostInfo():
		hostname = socket.gethostname()
		ipaddress = bytes(socket.gethostbyname(hostname),'utf8')
		return ipaddress

	def agentPoll():
		pollsig = b"$agent-poll$"
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print(f"attempting to connect to firecontroller at {HOST}")
		s.connect((HOST,PORT))
		print("connection successful")
		s.sendall(pollsig)
		print("polling firecontroller")
		data = s.recv(1024)
		if not data:
			print("polling failed, cannot find firecontroller")
		else:
			
			print("sending hostinfo")
			s.sendall(fireagent.getHostInfo())
			print("firecontroller msg ->" + repr(data.decode()))
			status = s.recv(1024)
			print("firecontroller msg ->" + repr(status.decode()))			
		s.close()
		time.sleep(1)
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((HOST,PORT))
		s.sendall(b"$agent-config$")
		command = s.recv(1024)
		commandResult = str(os.popen(command.decode()).read())
		s.sendall(bytes(commandResult, 'UTF-8'))
		print(commandResult)
		#fireagent.serverCommands()	

	def serverCommands():
		agentsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		bind = agentsocket.bind((socket.gethostname(),5050))
		agentsocket.listen()
		while True:
			print("waiting on server commands")
			(serversocket, address) = agentsocket.accept()
			auth = serversocket.recv(1024)
			if auth.startswith(b"$server-auth$"):
				commands = serversocket.recv(1024)
				decoded = commands.decode()
				for i in commands:
					command = s.recv(1024)
					print("recieved command from server")
					#time.sleep(1)
					commandResult = str(os.popen(command.decode()).read())
					s.sendall(bytes(commandResult, 'UTF-8'))
				print(commandResult)

fireagent.agentPoll()
fireagent.serverCommands()


