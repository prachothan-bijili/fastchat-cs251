import select
import socket
import sys
import queue
import psycopg2
import json
import random
import os
from handler import handler

class Server:
    """
    | Server of Client-Server Program connected via sockets, gets inputs from clients, to allow them to send and receive messages, authenticate them and save data in database
    """
    
    def __init__(self):
        """
        | Constructor method
        """

        try:
            os.mkdir('pems')
        except:
            pass
        self.host = "127.0.0.1"
        # ports that each server will bind to
        self.port = [60000,50000,40000,30000,20000]
        self.server_address = [(self.host,self.port[0]),(self.host,self.port[1]),(self.host,self.port[2]),(self.host,self.port[3]),(self.host,self.port[4])]
        self.listen_value = 10
        # port that superserver will bind to
        self.superport = 6000
        self.super_sever_address = [(self.host, self.superport)]
        self.listen_value = 10
        self.super_sever_address = [(self.host, self.superport)]
        # setting up a socket that acts as a superserver by telling client which port to connect to
        print("Trying to setup superserver")
        self.superserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.superserver.setblocking(0)
        try:               
            self.superserver.bind((self.host, self.superport))
            print ('starting up super server on port', self.superport)
            self.superserver.listen(self.listen_value)
        except :
            print("Port is busy")
            return
        # setting up servers for clients to connect to, redirected by superserver
        self.servers=[]
        for i in range(0,5):
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setblocking(0)
            try:               
                server.bind((self.host,self.port[i]))
                print ('starting up on %s port %s' % self.server_address[i])
                server.listen(self.listen_value)
                self.servers.append(server)           
            except :
                print("Port is busy")
                return
        # connect the server to database
        try:
            self.conn = psycopg2.connect("dbname=fastchatdb user=fastchat password=codebrewers")    
            self.cursor = self.conn.cursor()
            print("Database connection successful")
        except psycopg2.DatabaseError as e:
            print('Error code {}: {}'.format(e.pgcode, e))    
            print("Cannot connect to the database")
            sys.exit(1)
        self.inputs = [self.superserver]  
        # map of servers to port it is binded to
        self.port_con = {}                                   
        # map of servers to how many clients connected to this server
        self.port_con_count = {}                             
        self.port_con_count[self.superserver] = 0
        for s in range(len(self.servers)):
            self.inputs.append(self.servers[s])
            self.port_con[self.servers[s]] = self.port[s]
            self.port_con_count[self.servers[s]] = 0

    def getPort(self):
        """
        | Returns the port that has minimum number of clients connected to it 

        :return: Port number
        :rtype: int

        """

        min_con = self.port_con_count[self.servers[0]]
        min_server = self.servers[0]
        for s in range(len(self.servers)):
            if self.port_con_count[self.servers[s]] < min_con:
                min_con = self.port_con_count[self.servers[s]]
                min_server = self.servers[s]
        self.port_con_count[min_server] += 1
        return self.port_con[min_server]

    def run_server(self):
        """
        | Connects client to a port named as superport and return port number having minimum number of clients and allow clients to send or receive messages
        """

        # maps sockets to user IDs
        id_dict = {}                                    
        # maps client socket to the server ports
        which_port = {}                                 

        try:
            while self.inputs:

                # Wait for at least one of the sockets to be ready for processing     
                readable, writable, exceptional = select.select(self.inputs,[], self.inputs)
                # Handle inputs
                for s in readable:
                    # accept connection from superserver
                    if s is self.superserver: 
                        connection, client_address = s.accept()
                        print ('connection to superserver from', client_address)
                        self.port_con_count[self.superserver] +=1
                        which_port[connection] = s
                        # doesnt wait for anything to complete
                        connection.setblocking(0) 
                        self.inputs.append(connection)                
                    else:
                        is_new = 0
                        # accept connection to one of server assigned to user by superserver
                        for k in self.servers:
                            if s is k:    
                                is_new = 1                                                         
                                # A "readable" server socket is ready to accept a connection
                                connection, client_address = s.accept()
                                print ('new connection from', client_address)
                                which_port[connection] = s
                                # doesnt wait for anything to complete
                                connection.setblocking(0)    
                                self.inputs.append(connection) 
                                
                        if not is_new:      
                            try:
                                # handles user inputs, login, signup, create group, send messagem etc and saves data in database
                                b = handler(s,self.cursor,id_dict,self.getPort)    
                            except KeyboardInterrupt:
                                # close connection of each server
                                for serv in self.servers:
                                    serv.close()
                                self.conn.close()
                                return
                            if not b: 
                                # removes count of clients connected to the port to which client was connected to
                                self.port_con_count[which_port[s]] -= 1
                                self.inputs.remove(s)
                                s.close()                        
                                
                                print('closing', client_address, 'after reading no data')
                # Handle "exceptional conditions"
                for s in exceptional:
                    print ('handling exceptional condition for', s.getpeername())
                    # Stop listening for input on the connection
                    self.inputs.remove(s)            
                    del id_dict[s]
                    s.close()
        except :
            
            for keys in id_dict:
                kill_info = {"info-type":"kill"}
                kill_info = json.dumps(kill_info)        
                keys.sendall(kill_info.encode())
            
            for serv in self.servers:
                serv.close()            
            self.conn.close()
            return
    
if __name__ == "__main__":
    server = Server()
    server.run_server()
