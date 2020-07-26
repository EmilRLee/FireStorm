#!/usr/bin/bash

import os, time, socket, yaml, argparse

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
        agent_config = firesocket.recv(1024)
        print("fire_server -> " + agent_config.decode())

    def update(agent):
        firesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        firesocket.connect((HOST,PORT))
        print(f"attempting to connect to firecontroller at {HOST}")
        firesocket.sendall(b"$push-config$")
        status = firesocket.recv(1024)
        print("fire_server ->\n" + status)

def main():

    parser = argparse.ArgumentParser(description='firewall-cmd/Netfilter firewall configration')
    parser.add_argument("-listagents", help="lists registered agents", action="store_true")
    parser.add_argument("-getconfig", help="lists registered agents", action="store")
    parser.add_argument("-update", help="updates the agents current configurations", action="store")
    args = parser.parse_args()
    
    if args.listagents:
        firecontrol.list_agents()
    if args.getconfig:
        agent = args.getconfig
        firecontrol.get_config(agent)
    if args.update:
        agent = args.update
        firecontrol.update(agent)
if __name__ == "__main__":
    # execute only if run as a script
    main()