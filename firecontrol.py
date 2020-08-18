#!/usr/bin/bash

import os, time, socket, yaml, argparse,sys, subprocess, pickle, ssl
from flask import Flask, request, render_template, abort, redirect, url_for


PORT = 5050
#HOST = '192.168.5.24'
app = Flask(__name__,template_folder='ui/templates', static_folder='ui/static')

def agentinfo(HOST,agent):
    print(f"agent ========= {agent}")
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations("./certs/cacert.crt")
    firesocket = context.wrap_socket(conn, server_hostname="FireStorm", server_side=False)
    firesocket.connect((HOST,PORT))
    firesocket.sendall(b'$agent-table$')
    #after connect send agent ip to get its iptables
    time.sleep(10)
    firesocket.sendall(bytes(str(agent),'UTF-8'))
    
    with open("{}.iptable".format(agent), "wb") as iptable:
        agentconfig = firesocket.recv(65535)
        iptable.write(agentconfig)



def webvars(HOST):
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations("./certs/cacert.crt")
    firesocket = context.wrap_socket(conn, server_hostname="FireStorm", server_side=False)
    firesocket.connect((HOST,PORT))
    firesocket.sendall(b"$init-web$")
    pickled_active_agents = firesocket.recv(1024)
    pickled_inactive_agents = firesocket.recv(1024)
    serverName = firesocket.recv(1024)
    pickled_fire_agents = firesocket.recv(1024)
    pickled_startTime = firesocket.recv(1024)
    startTime = pickle.loads(pickled_startTime)
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



    return HOST, active_agents, inactive_agents, serverName, fire_agents, AgentCount, startTime



@app.route("/home",)
def web_home():
    HOST, active_agents, inactive_agents, serverName, fire_agents, AgentCount, startTime = webvars(app.config['HOST'])
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

    UpTime = time.time() - startTime

    return render_template("home.html", host=HOST, activeCount=activeCount, active_agents=active_agents, inactiveCount=inactiveCount, inactive_agents=inactive_agents, serverName=serverName, AgentCount=AgentCount, fire_agents=fire_agents, UpTime=UpTime)

@app.route("/agents/<agent>/", methods=['GET','POST'])
def agent(agent):
    
    agentinfo(app.config['HOST'],agent)

    with open("{}.iptable".format(agent), "r") as file:
        agentconfig = file.readlines()
    
    if request.method == "POST":
		
        updatedconfig = request.form['config']

        with open("{}.iptable".format(agent), "w+") as file:
            file.write(updatedconfig)
            print("UPDATED TABLE")
        file.close
        #flash(attempted_username)
        #flash(attempted_password)

        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_verify_locations("./certs/cacert.crt")
        firesocket = context.wrap_socket(conn, server_hostname="FireStorm", server_side=False)
        firesocket.connect((app.config['HOST'],PORT))
        print(f"attempting to connect to firecontroller at {app.config['HOST']}")
        firesocket.sendall(b"$push-config$")
        status = firesocket.recv(1024)
        print("fire_server ->\n" + status.decode())
        #need to send the name of file first then file.
        agntable = agent + ".iptable"
        firesocket.sendall(bytes(agntable, 'UTF-8'))
        firesocket.sendall(bytes(updatedconfig,'UTF-8'))

            
        print("file sent")

        status = firesocket.recv(1024)
        print("fire_server ->\n" + status.decode())
        firesocket.close()
        print(updatedconfig)
        return redirect(url_for('agent', agent=agent))
    else:			
        return render_template("agentinfo.html", agent=agent, agentconfig=agentconfig)


@app.route("/agents")
def listagents():
    #### xxx Needs ATTENTION vvvvvvvvvvvvvv need to change to platform agnostic
    agents = subprocess.run("c:/Users/DracoThaKing/AppData/Local/Programs/Python/Python38-32/python.exe firecontrol.py -listagents", check=True, stdout=subprocess.PIPE , universal_newlines=True)

    return agents.stdout


class firecontrol:


    def list_agents(HOST):

        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_verify_locations("./certs/cacert.crt")
        firesocket = context.wrap_socket(conn, server_hostname="FireStorm", server_side=False)
        firesocket.connect((HOST,PORT))
        print(f"attempting to connect to firecontroller at {HOST}")
        firesocket.sendall(b"$list-agent$")
        status = firesocket.recv(1024)
        agents = firesocket.recv(1024)
        print("fire_server -> " + status.decode())
        agents = print("fire_server -> " + agents.decode())
        return 0
        
    def get_config(HOST,agent):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_verify_locations("./certs/cacert.crt")
        firesocket = context.wrap_socket(conn, server_hostname="FireStorm", server_side=False)
        firesocket.connect((HOST,PORT))
        print(f"attempting to connect to firecontroller at {HOST}")
        firesocket.sendall(b"$get-config$")
        status = firesocket.recv(1024)
        print("fire_server -> " + status.decode())
        #send agent ip to retrieved its configs
        firesocket.sendall(bytes(str(agent), 'UTF-8'))
        config_status = firesocket.recv(65535)
        print("fire_server -> " + config_status.decode())
        if config_status != b"agent not registered":
            
            iptable_config = firesocket.recv(65535)
            with open("{}.iptable".format(agent), 'w+') as file1:
                file1.write(iptable_config.decode())
            print("RULES ->\n" + iptable_config.decode())
        else:
            print(config_status.decode())           

    def update(HOST,agent):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_verify_locations("./certs/cacert.crt")
        firesocket = context.wrap_socket(conn, server_hostname="FireStorm", server_side=False)
        firesocket.connect((HOST,PORT))
        print(f"attempting to connect to firecontroller at {HOST}")
        firesocket.sendall(b"$push-config$")
        status = firesocket.recv(1024)
        print("fire_server ->\n" + status)

    def server_stop(HOST):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_verify_locations("./certs/cacert.crt")
        firesocket = context.wrap_socket(conn, server_hostname="FireStorm", server_side=False)
        firesocket.connect((HOST,PORT))
        print(f"attempting to connect to firecontroller at {HOST}")
        firesocket.sendall(b"$server-stop$")
        status = firesocket.recv(1024)
        print("fire_server ->\n" + status.decode())

    def pushconfig(HOST,config):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_verify_locations("./certs/cacert.crt")
        firesocket = context.wrap_socket(conn, server_hostname="FireStorm", server_side=False)
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
            print(bytestosend)
        print("file sent")

        status = firesocket.recv(1024)
        print("fire_server ->\n" + status.decode())
        agent_status = firesocket.recv(1024)
        print(f"fire_server -> {agent_status.decode()}") 
        firesocket.close()


def main():

    parser = argparse.ArgumentParser(description='firewall-cmd/Netfilter firewall configration')
    parser.add_argument("-listagents", help="lists registered agents", action="store_true")
    parser.add_argument("-getconfig", help="request registered agents config file", action="store")
    parser.add_argument("-pushconfig", help="push new configuration file to agent", action="store")
    parser.add_argument("-server_stop", help="stops the fireserver", action="store_true")
    parser.add_argument("--web", help="initiates A web graphical interface. The app provides a graphical ui for configuring firewalls", action="store_true")
    parser.add_argument("-server", help="supply the fireserver IP", action="store")
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
        app.config['HOST'] = HOST
        app.run() 
        # --- testcase --> run webvars()        

if __name__ == "__main__":
    main()
