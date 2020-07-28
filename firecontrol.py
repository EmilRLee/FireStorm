#!/usr/bin/bash

import os, time, socket, yaml, argparse,sys


HOST = '192.168.5.24'
PORT = 5050


class firecontrol:

    

    def list_agents():

        firesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        firesocket.connect((HOST,PORT))
        print(f"attempting to connect to firecontroller at {HOST}")
        firesocket.sendall(b"$list-agent$")
        status = firesocket.recv(1024)
        agents = firesocket.recv(1024)
        print("fire_server -> " + status.decode())
        print("fire_server -> " + agents.decode())
        
    def get_config(agent):
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

    def update(agent):
        firesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        firesocket.connect((HOST,PORT))
        print(f"attempting to connect to firecontroller at {HOST}")
        firesocket.sendall(b"$push-config$")
        status = firesocket.recv(1024)
        print("fire_server ->\n" + status)

    def server_stop():
        firesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        firesocket.connect((HOST,PORT))
        print(f"attempting to connect to firecontroller at {HOST}")
        firesocket.sendall(b"$server-stop$")
        status = firesocket.recv(1024)
        print("fire_server ->\n" + status.decode())

    def pushconfig(agent):
        firesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        firesocket.connect((HOST,PORT))
        print(f"attempting to connect to firecontroller at {HOST}")
        firesocket.sendall(b"$push-config$")
        status = firesocket.recv(1024)
        print("fire_server ->\n" + status.decode())

        if agent.endswith(".yaml"):
            with open("{}".format(agent), "rb") as file:
                bytestosend = file.read(65535)
                firesocket.send(bytestosend)
        elif agent.endswith(".iptable"):
            with open("{}".format(agent), "rb") as file:
                bytestosend = file.read(65535)
                firesocket.send(bytestosend)

        status = firesocket.recv(1024)
        print("fire_server ->\n" + status.decode())

        
def main():

    parser = argparse.ArgumentParser(description='firewall-cmd/Netfilter firewall configration')
    parser.add_argument("-listagents", help="lists registered agents", action="store_true")
    parser.add_argument("-getconfig", help="lists registered agents", action="store")
    parser.add_argument("-pushconfig", help="updates the agents current configurations", action="store")
    parser.add_argument("-server_stop", help="stops the fireserver")
    args = parser.parse_args()
    
    if args.listagents:
        firecontrol.list_agents()
    if args.getconfig:
        agent = args.getconfig
        firecontrol.get_config(agent)
    if args.update:
        agent = args.update
        firecontrol.update(agent)
    if args.server_stop:
        firecontrol.server_stop()
if __name__ == "__main__":
    # execute only if run as a script
    main()
    
