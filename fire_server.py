#!/usr/bin/python3.6

import socket, sys, time, os, threading, schedule, pickle, netflow



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
            agentsocket.settimeout(20)
            print(f'connection from {address}')
            #self.serversocket.setblocking(False)
            #print("waiting for agents to connect")
            self.data = agentsocket.recv(1024)
            print(f"data recieved: {self.data.decode()}\n")
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
                    agentsocket.sendall(b"agent has configuration on file sending it now.")
                    #creates agents iptables config file for new agent
                    with open("./agents/{}.iptable".format(hostip), "rb") as conf:
                        agentconfig = conf.read(65535)
                        agentsocket.send(conf)
                   
                    self.agent_configs.append(hostip)
                    agentsocket.close()
                else:
                    agentsocket.sendall(b"fireserver has no configuration on file. pulling agent configuration now!") 
                   
                    #creates agents iptables config file for new agent
                    with open("./agents/{}.iptable".format(hostip), "wb") as create:
                        agentconfig = agentsocket.recv(65535)
                        create.write(agentconfig)
                   
                    self.agent_configs.append(hostip)
                    agentsocket.close()
            elif self.data.startswith(b"$agent-push$"):
                agentsocket.sendall(b"agent config request recieved")
                hostip = agentsocket.recv(1024)
                print(f"config push requested from agent: {hostip} from address {address[0]}")
                agentconfig = agentsocket.recv(65535)
                with open("./agents/{}.iptable".format(hostip), "wb") as create:
                    create.write(agentconfig)

                print("wrote to config")
                agentsocket.send(b"configuration successfull saved!")
            elif self.data.startswith(b"$list-agent$"):
                print(f"agentlist requested from {address}")
                agentsocket.sendall(b"agent list recieved")
                agents = self.getAgents()
                agentscount = len(agents)
                if agentscount > 0 :
                    agentsocket.sendall(bytes(str(fire_server.fire_agents),encoding='utf-8'))
                else:
                    agentsocket.sendall(b"no agents registered")
                agentsocket.close()
            elif self.data.startswith(b"$get-config$"):
                self.fire_controller = address
                print(f"agent config requested from {address}")
                agentsocket.sendall(b"agent config request recieved")
                #listen for agent IP recieved from firecontroller
                self.data = agentsocket.recv(1024)
                agent = self.data.decode()
                #process agent IP
                if agent in self.fire_agents:
                   
                    agentraw = open(r"./agents/{}.iptable".format(agent), "r")
                    agentsocket.sendall(bytes(agentraw.read(65535), "UTF-8"))
                    print(f"agent = {agent}")   
                else:
                    print(f'agent: {agent} not registered')
                    agentsocket.sendall(b"agent not registered")
                agentsocket.close()
            elif self.data.startswith(b"$server-stop$"):
                agentsocket.sendall(b"shutdown signal recieved")
                sys.exit()
            elif self.data.startswith(b"$push-config$"):
                agentsocket.sendall(b"configuration push recieved. processing .....")
                filename = agentsocket.recv(1024)
                config = agentsocket.recv(65535)
                if b"iptable" in filename:
                    with open("./agents/{}".format(filename.decode()), "w") as file:
                        file.write(config.decode().replace("\r\n","\n"))
                    agentsocket.sendall(bytes("configuration successfully saved", 'UTF-8'))
                    f = filename.decode().split(".iptable")
                    print(f"connecting to agent @ {f[0]}")
                    newagentsocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    #time.sleep(1)
                    try:
                        newagentsocket.connect((f[0],5050))
                        agentsocket.sendall(b"$server-auth$")
                        time.sleep(3)
                        print("sending configtype to agent")
                        newagentsocket.sendall(b'iptable')
                        with open("./agents/{}".format(filename.decode()), "r") as file:
                            bytestosend = file.read(65535)
                            newagentsocket.send(bytes(bytestosend,'UTF-8'))
                            print(f'SENT FILE TO {f[0]}')
                        time.sleep(3)
                        newagentsocket.sendall(bytes("iptables-restore agent.iptable", 'UTF-8'))
                        #status = agentsocket.recv(1024)
                        #print(f"status: {status}")
                    except socket.error:
                        print(socket.error)
                        agentsocket.sendall(b"agent could not be reached at the moment. Must wait for agent to poll for changes to take affect")
                        continue
                    agentsocket.close()
                
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
                agentsocket.close()
            elif self.data.startswith(b'$agent-table'):
                print("agent table request recieved")
                agent = agentsocket.recv(1024)
                print(agent.decode())
                print("agent = {}".format(agent.decode()))
                with open('./agents/{}.iptable'.format(agent.decode()), 'rb') as agentconfig:
                    agentconf = agentconfig.read(65535)
                    agentsocket.sendall(agentconf)
                agentsocket.close()
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
                
def main():

    
    Fireserver = fire_server()
    Fireserver.socket_comms()
    

if __name__ == "__main__":
    # execute only if run as a script
    main()
