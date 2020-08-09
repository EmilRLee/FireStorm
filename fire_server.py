#!/usr/bin/python3.6

import socket, sys, time, yaml, os, threading, schedule, pickle



class fire_server:

    active_agents = []
    inactive_agents = []
    fire_agents = []
    agent_configs = []
    fire_controller = []
    data = []
    startTime = time.time()
    

    def __init__(self):
        print("making socket")
        self.serversocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        bind = self.serversocket.bind((socket.gethostname(),5050))
        self.serversocket.listen()
        if os.environ['COMPUTERNAME']:
            self.serverName = os.environ['COMPUTERNAME']
        else:
            self.serverName = os.environ['HOSTNAME']
        
    def __del__(self):
        print('Server deleted')   
    
    def heartbeat(self,agentinfo):
        while True:
            time.sleep(60)
            try:
                serversocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                serversocket.connect((agentinfo,5050))
                serversocket.close()
                if agentinfo not in self.active_agents:
                    #add agent to active state
                    self.active_agents.append(agentinfo)
                print(self.active_agents)
                if agentinfo in self.inactive_agents:
                    #remove agent from inactive state
                    self.inactive_agents.remove(agentinfo)
            except socket.error:
                print(f'agent {agentinfo} has no response')
                if agentinfo in self.active_agents:
                    self.active_agents.remove(agentinfo)
                    if agentinfo not in self.inactive_agents:
                        self.inactive_agents.append(agentinfo)

    def socket_comms(self):       
        while True:
            print("waiting for agents to connect")
            (agentsocket, address) = self.serversocket.accept()
            agentsocket.settimeout(10)
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
                #agent sends host info vvv
                data = self.data.decode()
                status = self.agentCheck(data)
                agentsocket.sendall(status)
                agentsocket.close()
                print(self.getAgents())
            elif self.data.startswith(b"$agent-config$"):
            #sent from agents to get initial configuration when it starts up.    
                print("config-requested")
                hostip = agentsocket.recv(1024)
                hostip = hostip.decode()
                if hostip in self.agent_configs:
                    print("reading configuration from {}.yaml".format(hostip))
                    file = open("./agents/{}.yaml".format(hostip), "r")
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
                    with open("./agents/{}.iptable".format(hostip), "wb") as create:
                        agentconfig = agentsocket.recv(65535)
                        totalRecv = len(agentconfig)
                        print(totalRecv)
                        create.write(agentconfig)
                    print("creating yaml config file for new agent")
                    #creates agents yaml config file for new agent
                    copy = open(r"./agents/baseconfig.yaml", "r")
                    with open("./agents/{}.yaml".format(hostip), "w+") as config:
                        for line in copy:
                            config.write(line)

                    self.agent_configs.append(hostip)
                    agentsocket.close()
            elif self.data.startswith(b"$list-agent$"):
                print(f"agentlist requested from {address}")
                agentsocket.sendall(b"agent list recieved")
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
                    agentsocket.sendall(bytes(agentyaml.read(65535), "UTF-8"))
                    agentyaml.close()
                    agentraw = open(r"./agents/{}.iptable".format(agent), "r")
                    agentsocket.sendall(bytes(agentraw.read(65535), "UTF-8"))
                    print(f"agent = {agent}")   
                else:
                    print(f'agent: {agent} not registered')
                    agentsocket.sendall(b"agent not registered")
            elif self.data.startswith(b"$server-stop$"):
                agentsocket.sendall(b"shutdown signal recieved")
                sys.exit()
            elif self.data.startswith(b"$push-config$"):
                agentsocket.sendall(b"configuration push recieved. processing .....")
                filename = agentsocket.recv(1024)
                config = agentsocket.recv(65535)
                if b"iptable" in filename:
                    with open("./agents/{}".format(filename.decode()), "wb") as file:
                        file.write(config)
                    agentsocket.sendall(bytes("configuration successfully saved", 'UTF-8'))
                    f = filename.decode().split(".iptable")
                    print(f"connecting to agent @ {f[0]}")
                    agentsocket.close()
                    agentsocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    time.sleep(1)
                    try:
                        agentsocket.connect((f[0],5050))
                    except socket.error:
                        print(socket.error)
                        continue
                    agentsocket.sendall(b"$server-auth$")
                    agentsocket.sendall(b'iptable')
                    with open("./agents/{}".format(filename.decode()), "rb") as file:
                        bytestosend = file.read(65535)
                        agentsocket.send(bytestosend)
                    agentsocket.sendall(bytes("iptables-restore agent.iptable", 'UTF-8'))
                    status = agentsocket.recv(1024)
                    print(f"status: {status}")
                elif b"yaml" in filename:
                    with open("./agents/{}".format(filename.decode()), "wb") as file:
                        file.write(config)
                    agentsocket.sendall(b"configuration successfully saved")
                    #cancel socket and connect to agent to notifiy agent of new firewall configuration.
                    f = filename.decode().split(".yaml")
                    print(f"connecting to agent @ {f[0]}")
                    agentsocket.close()
                    agentsocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    agentsocket.connect((f[0],5050))
                    agentsocket.sendall(b"$server-auth$")
                    agentsocket.sendall(b'yaml')
                    check, command = fire_server.command_build(filename.decode())
                    print(check)
                    print(command)
                    agentsocket.sendall(bytes("{}".format(check), 'UTF-8'))
                    checkstatus = agentsocket.recv(1024)
                    if checkstatus.decode().startswith("false"):
                        agentcommand = agentsocket.sendall(bytes(command, 'UTF-8'))
                        print(f"command sent: {command}")
                    else:
                        agentsocket.sendall(bytes('iptables -L', 'UTF-8'))
                        print('command sent: iptables -L')
            elif self.data.startswith(b'$init-web$'):
                
                active_agents = pickle.dumps(self.active_agents)
                inactive_agents = pickle.dumps(self.inactive_agents)
                fire_agents = pickle.dumps(self.fire_agents)

                if self.active_agents == []:
                    agentsocket.sendall(b'none')
                else:   
                    agentsocket.sendall(active_agents)
                time.sleep(.8)
                if self.inactive_agents == []:
                    agentsocket.sendall(b'none')
                else:
                    agentsocket.sendall(inactive_agents)
                time.sleep(.8)
                agentsocket.sendall(bytes(str(self.serverName), 'UTF-8'))
                time.sleep(.8)
                print(self.serverName)
                if self.fire_agents == []:
                    agentsocket.sendall(b'none')
                else:
                    agentsocket.sendall(fire_agents)
                startTime = pickle.dumps(self.startTime)
                agentsocket.sendall(startTime)
            #---- end of processing access keystring ----# 
            else:
                print("processing error")

    def agentCheck(self,agentinfo):

        if agentinfo in self.fire_agents:
            print("agent already registered")
            return b"agent already registered"
        else:
            self.fire_agents.append(agentinfo)
            self.active_agents.append(agentinfo)
            t = threading.Timer(20, self.heartbeat,[agentinfo])
            t.setDaemon(True)
            t.start()
            print("registered agent successfully")
            return b"agent registered successfully"

    def getAgents(self):
        return self.fire_agents

    def agentConfig(self,agent):
        if agent in self.fire_agents:
            index = self.fire_agents.index(agent)
            return self.fire_agents[index]

    def command_build(configfile):
        file = open("./agents/{}".format(configfile), "r")
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
            return  check, command                              

def main():

    
    Fireserver = fire_server()
    Fireserver.socket_comms()
    

if __name__ == "__main__":
    # execute only if run as a script
    main()
