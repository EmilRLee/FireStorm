#!/usr/bin/python3.6

import socket, sys, struct, os, time, pickle, argparse, netifaces, threading


PORT = 5050

class fireagent:


	def getHostInfo(interface):
		addr = netifaces.ifaddresses(interface)
		inet_addr = addr[netifaces.AF_INET][0]

		for key, value in inet_addr.items():
			if key == 'addr':
				return bytes(value,'UTF-8')	

		return ipaddress

	def agentInit(SERVER,interface):
		pollsig = b"$agent-poll$"
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print(f"attempting to connect to firecontroller at {SERVER}")
		s.connect((SERVER,PORT))
		print("connection successful")
		s.sendall(pollsig)
		print("polling firecontroller")
		data = s.recv(1024)
		if not data:
			print("polling failed, cannot find firecontroller")
		else:
			
			print("sending hostinfo ipaddress")
			hostip = fireagent.getHostInfo(interface)
			s.sendall(hostip)
			print("firecontroller msg ->" + repr(data.decode()))
			status = s.recv(1024)
			print("firecontroller msg ->" + repr(status.decode()))			
		s.close()
		time.sleep(1)
		fireagent.get_conf(SERVER,interface)
		
	def get_conf(SERVER,interface):
		while True:
			hostip = fireagent.getHostInfo(interface)
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			try:
				s.connect((SERVER,PORT))
				s.sendall(b"$agent-config$")
				s.sendall(hostip)
				status = s.recv(1024)
				if status.decode() == "agent has configuration on file sending it now.":
					conf = s.recv(65535)
					with open("agent.iptable", "wb") as rule:
						rule.write(conf)
					
			
					restore = os.popen("iptables-restore agent.iptable").read()
					s.sendall(bytes(restore, 'UTF-8'))
					s.close()
				else:
					os.system("iptables-save > agent.iptable")
					time.sleep(1)
					with open("./agent.iptable", "rb") as file:
						conf = file.read(65535)
						print(conf.decode("UTF-8"))
						s.send(conf)
			except:
				continue
			time.sleep(60)
	#push agents current configurations to the server
	def push_conf(SERVER):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((SERVER,PORT))
		s.sendall(b"$agent-push$")
		stat = s.recv(1024)
		print(stat.decode())
		s.sendall(hostip)
		
		os.popen("iptables-save > agent.iptable")
		with open("agent.iptable", "rb") as file:
			conf = file.read(65535)
			print(conf.decode("UTF-8"))
			s.send(conf)
		stat = s.recv(1024)
		print(stat.decode())
	def agentPoll(SERVER,interface):
		while True:
			pollsig = b"$agent-poll$"
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			print(f"attempting to connect to firecontroller at {SERVER}")
			try:
				s.connect((SERVER,PORT))
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
			except:
				print(socket.error)
				continue			
			time.sleep(60)


	def serverCommands(SERVER,interface):
        
		hostip = fireagent.getHostInfo(interface)
		agentsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		bind = agentsocket.bind((hostip,5050))
		agentsocket.listen()
		
		while True:
			print("waiting on server commands")
			(serversocket, address) = agentsocket.accept()
			print("connection recieved from " + address[0])
			auth = serversocket.recv(1024)
			configtype = serversocket.recv(1024)
			print("CONFIG TYPE" + configtype.decode())
			if auth.startswith(b"$server-auth$"):
		
				if configtype == b'iptable':	
					configfile = serversocket.recv(65535)
					with open("agent.iptable", "w") as file:
						file.write(configfile.decode().replace("\r\n","\n"))
						#print(file.read(65535))
					print('WROTE TO FILE')
					command = serversocket.recv(1024)
					print("command recieved: "  + command.decode())
					os.popen(command.decode())
				serversocket.close()
				

def main():
	parser = argparse.ArgumentParser(description='firecontrol agent')
	parser.add_argument("-interface", help="interface the agent will listen for fire server", action="store")
	parser.add_argument("-server", help="fireStorm server to connect to.", action="store")
	args = parser.parse_args()

	SERVER = args.server

	if args.interface:
		interface = args.interface
		fireagent.agentInit(SERVER,interface)
		t = threading.Timer(20, fireagent.agentPoll,[SERVER,interface])
		t.setDaemon(True)
		t.start()
		fireagent.serverCommands(SERVER,interface)
	

if __name__ == "__main__":
    main()


