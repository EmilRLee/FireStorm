#!/usr/bin/python3.6

import socket, sys, struct, os, time, pickle, argparse, netifaces, threading, ssl


PORT = 5050

class fireagent:


	def getHostInfo(interface):
		addr = netifaces.ifaddresses(interface)
		inet_addr = addr[netifaces.AF_INET][0]

		for key, value in inet_addr.items():
			if key == 'addr':
				return bytes(value,'UTF-8')	
		#return ipaddress

	def agentInit(SERVER,interface):
		pollsig = b"$agent-poll$"
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print(f"attempting to connect to firecontroller at {SERVER}")
		context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
		context.verify_mode = ssl.CERT_REQUIRED
		context.load_verify_locations("./certs/cacert.crt")
		conn = context.wrap_socket(s, server_hostname="FireStorm", server_side=False)
		conn.connect((SERVER,PORT))
		print("connection successful")
		conn.sendall(pollsig)
		print("polling firecontroller")
		data = conn.recv(1024)
		if not data:
			print("polling failed, cannot find firecontroller")
		else:
			
			print("sending hostinfo ipaddress")
			hostip = fireagent.getHostInfo(interface)
			conn.sendall(hostip)
			print("firecontroller msg ->" + repr(data.decode()))
			status = conn.recv(1024)
			print("firecontroller msg ->" + repr(status.decode()))			
		conn.close()
		time.sleep(1)
		t = threading.Timer(1,fireagent.get_conf,[SERVER,interface])
		t.setDaemon(True)
		t.start()
		
	def get_conf(SERVER,interface):
		while True:
			hostip = fireagent.getHostInfo(interface)
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			try:
				context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
				context.verify_mode = ssl.CERT_REQUIRED
				context.load_verify_locations("./certs/cacert.crt")
				conn = context.wrap_socket(s, server_hostname="FireStorm", server_side=False)
				conn.connect((SERVER,PORT))
				conn.sendall(b"$agent-config$")
				conn.sendall(hostip)
				status = conn.recv(1024)
				
				if status == b"agent has configuration on file sending it now.":
					print(status)
					conf = conn.recv(65535)
					with open("agent.iptable", "w") as rule:
						conf = conf.decode().replace("\r\n", "\n").replace("\n\n", "\n")
						rule.write(conf)
						print("wrote to agent.iptable")
			
					os.system("iptables-restore agent.iptable")
					restore = os.popen("iptables-save").read()
					conn.sendall(bytes(restore, 'UTF-8'))
					conn.close()
				else:
					print(status)
					os.system("iptables-save > agent.iptable")
					time.sleep(1)
					with open("./agent.iptable", "rb") as file1:
						conf = file1.read(65535)
						print(conf.decode("UTF-8"))
						conn.send(conf)
				time.sleep(60)
			except:	
				time.sleep(60)
				continue
	#push agents current configurations to the server
	def push_conf(SERVER,interface):
		hostip = fireagent.getHostInfo(interface)
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
		context.verify_mode = ssl.CERT_REQUIRED
		context.load_verify_locations("./certs/cacert.crt")
		conn = context.wrap_socket(s, server_hostname="FireStorm", server_side=False)
		conn.connect((SERVER,PORT))
		conn.sendall(b"$agent-push$")
		stat = conn.recv(1024)
		print(stat.decode())
		conn.sendall(hostip)
		
		os.popen("iptables-save > agent.iptable")
		with open("agent.iptable", "rb") as file:
			conf = file.read(65535)
			print(conf.decode("UTF-8"))
			conn.send(conf)
		stat = conn.recv(1024)
		print(stat.decode())
	def agentPoll(SERVER,interface):
		while True:
			pollsig = b"$agent-poll$"
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			print(f"attempting to connect to firecontroller at {SERVER}")
			try:
				context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
				context.verify_mode = ssl.CERT_REQUIRED
				context.load_verify_locations("./certs/cacert.crt")
				conn = context.wrap_socket(s, server_hostname="FireStorm", server_side=False)
				conn.connect((SERVER,PORT))
				print("connection successful")
				conn.sendall(pollsig)
				print("polling firecontroller")
				data = conn.recv(1024)
				if not data:
					print("polling failed, cannot find firecontroller")
				else:
				
					print("sending hostinfo ipaddress")
					conn.sendall(fireagent.getHostInfo(interface))
					print("firecontroller msg ->" + repr(data.decode()))
					status = conn.recv(1024)
					print("firecontroller msg ->" + repr(status.decode()))
				conn.close()
				time.sleep(60)
			except socket.error or KeyboardInterrupt:
				if KeyboardInterrupt:
					sys.exit()
				else:
					continue			
			time.sleep(60)


	def serverCommands(SERVER,interface):
        
		hostip = fireagent.getHostInfo(interface)
		agentsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		bind = agentsocket.bind((hostip,5050))
		agentsocket.listen()
		context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
		context.load_cert_chain(certfile="./certs/agent_cacert.crt", keyfile="./certs/agent_cert.pem", password="mypass")  # 1. key, 2. cert, 3. intermediates
		#context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1  # optional
		context.set_ciphers('EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH')

		while True:
			print("waiting on server commands")
			try:
				(conn, address) = agentsocket.accept()
				serversocket = context.wrap_socket(conn, server_side=True)
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
			except:
				if KeyboardInterrupt:
					sys.exit()
				else:
					continue
				

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


