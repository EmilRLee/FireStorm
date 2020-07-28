#!/usr/bin/python3.6

import socket, sys, struct, time, yaml, os, pickle



class fire_server:

    fire_agents = []
    agent_configs = []
    fire_controller = []
    data = []
    
    def __init__(self):
        print("making socket")
        self.serversocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        bind = self.serversocket.bind((socket.gethostname(),5050))
        self.serversocket.listen()
        
    def __del__(self):
        print('Server deleted')
        

    def socket_comms(self):       
        while True:
            print("waiting for agents to connect")
            (agentsocket, address) = self.serversocket.accept()
            print(f'connection from {address}')
            #self.serversocket.setblocking(False)
            #print("waiting for agents to connect")
            self.data = agentsocket.recv(1024)
            print(f"data recieved: {self.data.decode()}")
            if not self.data:
                pass
            if self.data.startswith(b"$agent-poll$"):
                print("polling recieved")
                agentsocket.sendall(b"polling recieved")
                self.data = agentsocket.recv(1024)
                data = self.data.decode()
                status = self.agentCheck(data)
                agentsocket.sendall(status)
                agentsocket.close()
                print(self.getAgents())
            elif self.data.startswith(b"$agent-config$"):
            #sent from agents to get initial configuration when it starts up.    
                print("config-requested")
                if address[0] in self.agent_configs:
                    print("reading configuration from {}.yaml".format(address[0]))
                    file = open("./agents/{}.yaml".format(address[0]), "r")
                    documents = yaml.load(file)
                    count = 1
                    command = 'iptables'
                    check = 'iptables'
                    for key, value in documents.items():
                        count += 1
                        
                        if key == "table":
                            command = command + f' -t {value}'
                        elif key == "action":
                            check = command + ' -C'
                            if value == "append":
                                command = command + f' -A'
                            if value == "insert":
                                command = command + f' -I'
                        elif key == "chain":
                            command = command + ' {}'.format(value.upper())
                            check = check + ' {}'.format(value.upper())
                        elif key == "match":
                            vals = 0
                            for i in value:
                                try:
                                    if value[vals].get('protocol'):
                                        p = value[vals].get('protocol')
                                        print(value[vals].get('protocol'))
                                        command = command + f' -p {p}'
                                        check = check + f' -p {p}'
                                except KeyError:
                                    pass
                                try:
                                    if value[vals].get('dport'):
                                        d = value[vals].get('dport')
                                        print(value[vals].get('dport'))
                                        command = command + f' --dport {d}'
                                        check = check + f' --dport {d}'
                                except KeyError:
                                    pass
                                try:
                                    if value[vals].get('source'):
                                        s = value[vals].get('source')
                                        print(value[vals].get('source'))
                                        command = command + f' -s {s}'
                                        check = check + f' -s {s}'
                                except KeyError:
                                    pass
                                try:
                                    if value[vals].get('destination'):
                                        d = value[vals].get('destination')
                                        print(value[vals].get('destination'))
                                        command = command + f' -d {d}'
                                        check = check + f' -d {d}'
                                except KeyError:
                                    pass
                                try:
                                    if value[vals].get('module'):
                                        m = value[vals].get('module')
                                        print(value[vals].get('module'))
                                        command = command + f' -m {m}'
                                        check = check + f' -m {m}'
                                except KeyError:
                                    pass
                                vals += 1
                        elif key == 'target':
                            command = command + ' -j {}'.format(value.upper())
                            check = check + ' -j {}'.format(value.upper())    
                                
                    #agentsocket.sendall(bytes(str(documents), 'UTF-8'))
                    print(documents)
                    agentcheck = agentsocket.sendall(bytes(check, 'UTF-8'))
                    checkstatus = agentsocket.recv(1024)
                    print(checkstatus.decode())
                    if checkstatus.decode().startswith("false"):
                        agentcommand = agentsocket.sendall(bytes(command, 'UTF-8'))
                        print(f"command sent: {command}")
                    else:
                        agentsocket.sendall(bytes('iptables -L', 'UTF-8'))
                        print('command sent: iptables -L')
                    #time.sleep(1)
                    #commanddata = agentsocket.recv(4096)
                    #print(commanddata.decode())

                    file.close()
                    agentsocket.close()
                else:
                    
                    file = open(r"./agents/baseconfig.yaml", "r")
                        
                    documents = yaml.load(file)
                    count = 1
                    command = 'iptables'
                    check = 'iptables'
                    for key, value in documents.items():
                        count += 1
                        
                        if key == "table":
                            command = command + f' -t {value}'
                        elif key == "action":
                            check = command + ' -C'
                            if value == "append":
                                command = command + f' -A'
                            if value == "insert":
                                command = command + f' -I'
                        elif key == "chain":
                            command = command + ' {}'.format(value.upper())
                            check = check + ' {}'.format(value.upper())
                        elif key == "match":
                            vals = 0
                            for i in value:
                                try:
                                    if value[vals].get('protocol'):
                                        p = value[vals].get('protocol')
                                        print(value[vals].get('protocol'))
                                        command = command + f' -p {p}'
                                        check = check + f' -p {p}'
                                except KeyError:
                                    pass
                                try:
                                    if value[vals].get('dport'):
                                        d = value[vals].get('dport')
                                        print(value[vals].get('dport'))
                                        command = command + f' --dport {d}'
                                        check = check + f' --dport {d}'
                                except KeyError:
                                    pass
                                try:
                                    if value[vals].get('source'):
                                        s = value[vals].get('source')
                                        print(value[vals].get('source'))
                                        command = command + f' -s {s}'
                                        check = check + f' -s {s}'
                                except KeyError:
                                    pass
                                try:
                                    if value[vals].get('destination'):
                                        d = value[vals].get('destination')
                                        print(value[vals].get('destination'))
                                        command = command + f' -d {d}'
                                        check = check + f' -d {d}'
                                except KeyError:
                                    pass
                                try:
                                    if value[vals].get('module'):
                                        m = value[vals].get('module')
                                        print(value[vals].get('module'))
                                        command = command + f' -m {m}'
                                        check = check + f' -m {m}'
                                except KeyError:
                                    pass
                                vals += 1
                        elif key == 'target':
                            command = command + ' -j {}'.format(value.upper())
                            check = check + ' -j {}'.format(value.upper())
                        
                    #agentsocket.sendall(bytes(str(documents), 'UTF-8'))
                    print(documents)
                    file.close()
                    agentcheck = agentsocket.sendall(bytes(check, 'UTF-8'))
                    checkstatus = agentsocket.recv(1024)
                    print(checkstatus.decode())
                    if checkstatus.decode().startswith("false"):
                        agentcommand = agentsocket.sendall(bytes(command, 'UTF-8'))
                        print(f"command sent: {command}")
                    else:
                        agentsocket.sendall(bytes('iptables -L', 'UTF-8'))
                        print('command sent: iptables -L')
                    #time.sleep(1)
                    #commanddata = agentsocket.recv(4096)
                    #print(commanddata.decode())
                    #creates agents iptables config file for new agent
                    with open("./agents/{}.rules".format(address[0]), "wb") as create:
                        agentconfig = agentsocket.recv(65535)
                        totalRecv = len(agentconfig)
                        print(totalRecv)
                        create.write(agentconfig)
                    print("creating yaml config file for new agent")
                    #creates agents yaml config file for new agent
                    copy = open(r"./agents/baseconfig.yaml", "r")
                    with open("./agents/{}.yaml".format(address[0]), "w+") as config:
                        for line in copy:
                            config.write(line)

                    self.agent_configs.append(address[0])
                    agentsocket.close()
            elif self.data.startswith(b"$list-agent$"):
                print(f"agentlist requested from {address}")
                agentsocket.sendall(b"agent config push recieved")
                agents = self.getAgents()
                agentscount = len(agents)
                if agentscount > 0 :
                    agentsocket.sendall(bytes(str(fire_server.fire_agents),encoding='utf-8'))
                else:
                    agentsocket.sendall(b"no agents registered")
            elif self.data.startswith(b"$get-config$"):
                self.fire_controller = address
                print(f"agent config requested from {address}")
                agentsocket.sendall(b"agent config request recieved")
                #listen for agent IP recieved from firecontroller
                self.data = agentsocket.recv(1024)
                agent = self.data.decode()
                #process agent IP
                if agent in self.fire_agents:
                    agentyaml = open(r"./agents/{}.yaml".format(agent), "r")
                    agentsocket.sendall(bytes(f"/////yaml/////\n {agentyaml.read(65535)}\n : yaml -- ", "UTF-8"))
                    agentyaml.close()
                    agentraw = open(r"./agents/{}.rules".format(agent), "r")
                    agentsocket.sendall(bytes(f"/////iptable//////\n {agentraw.read(65535)}\n :iptable-- ", "UTF-8"))
                    print(f"agent = {agent}")
        
                    
                else:
                    print(f'agent: {agent} not registered')
                    agentsocket.sendall(b"agent not registered")
            elif self.data.startswith(b"$server-stop$"):
                agentsocket.sendall(b"shutdown signal recieved")
                sys.exit()
            else:
                print("processing error")

    def agentCheck(self,agentinfo):

        if agentinfo in self.fire_agents:
            print("agent already registered")
            return b"agent already registered"
        else:
            self.fire_agents.append(agentinfo)
            print("registered agent successfully")
            return b"agent registered successfully"

    def getAgents(self):
        return self.fire_agents

    def agentConfig(self,agent):
        if agent in self.fire_agents:
            index = self.fire_agents.index(agent)
            return self.fire_agents[index]

def main():

    
    Fireserver = fire_server()
    Fireserver.socket_comms()
    

if __name__ == "__main__":
    # execute only if run as a script
    main()
