#!/usr/bin/python3.6

import socket, sys, struct, os, time, pickle, argparse, netifaces

HOST = '192.168.5.24'
PORT = 5050

class fireagent:


	def getHostInfo(interface):
		addr = netifaces.ifaddresses(interface)
		inet_addr = addr[netifaces.AF_INET][0]

		for key, value in inet_addr.items():
			if key == 'addr':
				return value	


		return ipaddress

	def agentPoll(interface):
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
			
			print("sending hostinfo ipaddress")
			s.sendall(fireagent.getHostInfo(interface))
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
		s.close()

	def serverCommands(interface):
		
		
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
					check = serversocket.recv(1024)
					print(check.decode())
					checkstatus = os.system(check.decode())
					print(f'check: {checkstatus}')
					if checkstatus == 0:
						print('true')
						serversocket.sendall(bytes('true', 'UTF-8'))
						#print(str(checkstatus))
					else:	
						serversocket.sendall(bytes('false', 'UTF-8'))
					print('done')
					command = serversocket.recv(1024)
					os.popen(command.decode())
				elif configtype == b'iptable':	
					configfile = serversocket.recv(65535)
					with open("agent.iptable", "wb") as file:
						file.write(configfile)
					command = serversocket.recv(1024)
					os.popen(command.decode())
					serversocket.sendall(bytes(commandResult, 'UTF-8'))
				serversocket.close()
				fireagent.agentPoll()

def main():

	parser.add_argument("interface", help="interface the agent will listen for fire server", action="store")

	if args.interface:
		interface = args.interface
		fireagent.agentPoll(interface)
		fireagent.serverCommands()
	

if __name__ == "__main__":
    main()


