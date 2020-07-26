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
                print("config-requested")
                if address[0] in self.agent_configs:
                    print("reading configuration from {}.yaml".format(address[0]))
                    file = open(r"C:\Users\Dracothaking\Documents/Nscope Security/Fire_controller/Firecontroller/{}.yaml".format(address[0]), "r")
                    documents = yaml.full_load(file)
                    count = 1
                    for key, value in documents.items():
                        count += 1
                        print(count)
                    
                    #agentsocket.sendall(bytes(str(documents), 'UTF-8'))
                    print(documents)
                    for key, value in documents.items():
                        i = 1
                        calcval = i - 1
                        while (i <= count):
                            
                            command = agentsocket.sendall(bytes("firewall-cmd " + value[calcval], 'UTF-8'))
                            print(f"command sent: {value[calcval]}")
                            #time.sleep(1)
                            commanddata = agentsocket.recv(4096)
                            print(commanddata.decode())
                            i = i + 1
                            calcval = calcval + 1
                    agentsocket.close()
                else:
                    
                    file = open(r"C:\Users\Dracothaking\Documents/Nscope Security/Fire_controller/Firecontroller/baseconfig.yaml", "r")
                        
                    documents = yaml.load(file)
                    count = 1
                    command = 'iptables'
                    for key, value in documents.items():
                        count += 1
                        
                        if key == "table":
                            command = command + f' -t {value}'
                        elif key == "action":
                            if value == "append":
                                command = command + f' -D'
                        elif key == "match":
                            vals = 0
                            for i in value:
                                try:
                                    if value[vals].get('protocol'):
                                        p = value[vals].get('protocol')
                                        print(value[vals].get('protocol'))
                                        command = command + f' -p {p}'
                                except KeyError:
                                    pass
                                try:
                                    if value[vals].get('dport'):
                                        d = value[vals].get('dport')
                                        print(value[vals].get('dport'))
                                        command = command + f' --dport {d}'
                                except KeyError:
                                    pass
                                try:
                                    if value[vals].get('source'):
                                        s = value[vals].get('source')
                                        print(value[vals].get('source'))
                                        command = command + f' -s {s}'
                                except KeyError:
                                    pass
                                vals += 1
                        elif key == 'target':
                            command = command + ' -j {}'.format(upper(value))
                        
                    #agentsocket.sendall(bytes(str(documents), 'UTF-8'))
                    print(documents)
        
                    agentcommand = agentsocket.sendall(bytes(command, 'UTF-8'))
                    print(f"command sent: {command}")
                    #time.sleep(1)
                    commanddata = agentsocket.recv(4096)
                    print(commanddata.decode())

                    file.close()
                    print("creating config file for new agent")
                    #creates agents own config file
                    copy = open(r"C:\Users\Dracothaking\Documents/Nscope Security/Fire_controller/Firecontroller/baseconfig.yaml", "r")
                    with open("C:\\Users\\Dracothaking\\Documents/Nscope Security/Fire_controller/Firecontroller/{}.yaml".format(address[0]), "w+") as config:
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
                #listen for agent ip recieved from firecontroller
                self.data = agentsocket.recv(1024)
                agent = self.data.decode()
                if agent in self.fire_agents:
                    agentconf = open(r"{}.yaml".format(agent), "r")
                    agentsocket.sendall(bytes(f"{agentconf.read()}", "UTF-8"))
                    print(f"agent = {agent}")
                    
                else:
                    print(f'agent: {agent} not registered')
                    agentsocket.sendall(b"agent not registered")
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
