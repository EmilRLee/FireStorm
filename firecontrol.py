#!/usr/bin/bash

import os, time, socket, yaml, argparse,sys, subprocess, pickle
from flask import Flask, request, render_template


PORT = 5050
HOST = '192.168.5.24'
app = Flask(__name__,template_folder='ui/templates', static_folder='ui/static')

def webvars():
    firesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    firesocket.connect((HOST,PORT))
    firesocket.sendall(b"$init-web$")
    pickled_active_agents = firesocket.recv(1024)
    pickled_inactive_agents = firesocket.recv(1024)
    serverName = firesocket.recv(1024)
    pickled_fire_agents = firesocket.recv(1024)
   

    if pickled_active_agents != b'none':
        active_agents = pickle.loads(pickled_active_agents)
    else:
        active_agents = pickled_active_agents.decode()
    if pickled_inactive_agents != b'none':
        inactive_agents = pickle.loads(pickled_inactive_agents)
    else:
        inactive_agents = pickled_inactive_agents.decode()
    if pickled_fire_agents != b'none':    
        fire_agents = pickle.loads(pickled_fire_agents)
        AgentCount = len(fire_agents)
    else:
        fire_agents = pickled_fire_agents.decode()
        AgentCount = 0
    
    #--- TEST vvvvvvv
    

    # ---- TEST ^^^^^
    
    print(active_agents)
    print(inactive_agents)
    print(fire_agents)
    
    serverName = serverName.decode()
    print(serverName)
    print(AgentCount)



    return HOST, active_agents, inactive_agents, serverName, fire_agents, AgentCount



@app.route("/home")
def web_home():
    HOST, active_agents, inactive_agents, serverName, fire_agents, AgentCount = webvars()
    if active_agents != 'none':
        activeCount = len(active_agents)
    else:
        activeCount = 0
    if inactive_agents != 'none':
        inactiveCount = len(inactive_agents)
    else:
        inactiveCount = 0
    
    if active_agents == 'none':
        active_agents = 0
    if inactive_agents == 'none':
        inactive_agents = 'N/A'
    if fire_agents == 'none':
        fire_agents = ['No agents registered']
    return render_template("home.html", host=HOST, activeCount=activeCount, active_agents=active_agents, inactiveCount=inactiveCount, inactive_agents=inactive_agents, serverName=serverName, AgentCount=AgentCount, fire_agents=fire_agents)

@app.route("/listagents")
def web():
    agents = subprocess.run("c:/Users/DracoThaKing/AppData/Local/Programs/Python/Python38-32/python.exe firecontrol.py -listagents", check=True, stdout=subprocess.PIPE , universal_newlines=True)

    return agents.stdout


class firecontrol:


    def list_agents(HOST):

        firesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        firesocket.connect((HOST,PORT))
        print(f"attempting to connect to firecontroller at {HOST}")
        firesocket.sendall(b"$list-agent$")
        status = firesocket.recv(1024)
        agents = firesocket.recv(1024)
        print("fire_server -> " + status.decode())
        agents = print("fire_server -> " + agents.decode())
        return 0
        
    def get_config(HOST,agent):
        firesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        firesocket.connect((HOST,PORT))
        print(f"attempting to connect to firecontroller at {HOST}")
        firesocket.sendall(b"$get-config$")
        status = firesocket.recv(1024)
        print("fire_server -> " + status.decode())
        #send agent ip to retrieved its configs
        firesocket.sendall(bytes(str(agent), 'UTF-8'))
        agent_config = firesocket.recv(65535)
        print("fire_server -> " + agent_config.decode())
        with open("{}.yaml".format(agent), 'w+') as file:
            file.write(agent_config.decode())
        agent_config = firesocket.recv(65535)
        print("fire_server ->" + agent_config.decode())
        with open("{}.iptable".format(agent), 'w+') as file1:
            file1.write(agent_config.decode())

    def update(HOST,agent):
        firesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        firesocket.connect((HOST,PORT))
        print(f"attempting to connect to firecontroller at {HOST}")
        firesocket.sendall(b"$push-config$")
        status = firesocket.recv(1024)
        print("fire_server ->\n" + status)

    def server_stop(HOST):
        firesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        firesocket.connect((HOST,PORT))
        print(f"attempting to connect to firecontroller at {HOST}")
        firesocket.sendall(b"$server-stop$")
        status = firesocket.recv(1024)
        print("fire_server ->\n" + status.decode())

    def pushconfig(HOST,config):
        firesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        firesocket.connect((HOST,PORT))
        print(f"attempting to connect to firecontroller at {HOST}")
        firesocket.sendall(b"$push-config$")
        status = firesocket.recv(1024)
        print("fire_server ->\n" + status.decode())
        #need to send the name of file first then file.
        firesocket.sendall(bytes(config, 'UTF-8'))
        with open("{}".format(config), "rb") as file:
            bytestosend = file.read(65535)
            firesocket.send(bytestosend)
        print("file sent")

        status = firesocket.recv(1024)
        print("fire_server ->\n" + status.decode())


def main():

    parser = argparse.ArgumentParser(description='firewall-cmd/Netfilter firewall configration')
    parser.add_argument("-listagents", help="lists registered agents", action="store_true")
    parser.add_argument("-getconfig", help="lists registered agents", action="store")
    parser.add_argument("-pushconfig", help="updates the agents current configurations", action="store")
    parser.add_argument("-server_stop", help="stops the fireserver", action="store_true")
    parser.add_argument("--web", help="initiates the web app interface. The app provides a graphical ui for configuring firewalls", action="store_true")
    parser.add_argument("server", help="supply the fireserver IP", action="store")
    args = parser.parse_args()
    
    HOST = args.server

    if args.listagents:
        firecontrol.list_agents(HOST)
    if args.getconfig:
        agent = args.getconfig
        firecontrol.get_config(HOST,agent)
    if args.pushconfig:
        config = args.pushconfig
        firecontrol.pushconfig(HOST,config)
    if args.server_stop:
        firecontrol.server_stop(HOST)
    if args.web:
        app.run() 
        # --- testcase --> run webvars()        

if __name__ == "__main__":
    main()
