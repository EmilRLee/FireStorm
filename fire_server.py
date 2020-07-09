#!/usr/bin/python3.6

import socket, sys, struct, time, yaml, os



class fire_server:

    fire_agents = []
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
                file = open(r"C:\Users\Dracothaking\Documents/Nscope Security/Fire_controller/agentconfig.yaml", "r")
                documents = yaml.full_load(file)
                
                count = 0
                for key, value in documents.items():
                    count += 1
                    print(count)
                agentsocket.sendall(bytes([count]))
                for key, value in documents.items():
                    i = 0
                    command = agentsocket.sendall(bytes("firewall-cmd " + value[i], 'UTF-8'))
                    print(f"command sent: {command}")
                    #time.sleep(1)
                    commanddata = agentsocket.recv(1024)
                    print(commanddata.decode())
                    i += 1
                agentsocket.close()
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

    def getAgents(self,):
        return self.fire_agents

    
def main():

    
    Fireserver = fire_server()
    Fireserver.socket_comms()
    

if __name__ == "__main__":
    # execute only if run as a script
    main()
