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
		check = s.recv(1024)
		print(check.decode())
		checkstatus = os.system(check.decode())
		print(f'check: {checkstatus}')
		if checkstatus == 0:
			print('true')
			s.sendall(bytes('true', 'UTF-8'))
			#print(str(checkstatus))
		else:	
			s.sendall(bytes('false', 'UTF-8'))
		print('done')
		command = s.recv(1024)
		os.popen(command.decode())
		#s.sendall(bytes(commandResult, 'UTF-8'))
		os.popen("iptables-save > agent.iptable")
		time.sleep(3)
		with open("agent.iptable", "rb") as rule:
			bytestosend = rule.read(65535)
			s.send(bytestosend)

	def serverCommands():
		agentsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		bind = agentsocket.bind((socket.gethostname(),5050))
		agentsocket.listen()
		while True:
			print("waiting on server commands")
			(serversocket, address) = agentsocket.accept()
			auth = serversocket.recv(1024)
			if auth.startswith(b"$server-auth$"):
				configtype = serversocket.recv(1024)
				if configtype == b'yaml':
					check = s.recv(1024)
					print(check.decode())
					checkstatus = os.system(check.decode())
					print(f'check: {checkstatus}')
					if checkstatus == 0:
						print('true')
						s.sendall(bytes('true', 'UTF-8'))
						#print(str(checkstatus))
					else:	
						s.sendall(bytes('false', 'UTF-8'))
					print('done')
					command = s.recv(1024)
					os.popen(command.decode())
				elif configtype == b'iptable':	
					command = agentsocket.recv(1024)
					commandResult = str(os.popen(command.decode()).read())
					s.sendall(bytes(commandResult, 'UTF-8'))
				print(commandResult)
				fireagent.agentPoll()

fireagent.agentPoll()
fireagent.serverCommands()


