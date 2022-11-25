# fastchat-cs251
## Team memebers 
  * Vinu Rakav S
  * Prachothan Bijili 
  * Tulsiram


## Implemented So far:
### DataBase: PostgreSQL 
  * Consists of 4 tables
     * USERS -> Details of each user
     * MSG -> All messages
     * GRP -> Details of group
     * GRP_MEMB -> Members of a group

### Multi-Client Multi-Server connection: SELECT and Threading
  * Multiple client multiple server implemented by using selectors and threading
  * Client will be connected to superserver(a port reserved for superserver) and superserver will return the port having minimum number of clients connected to this port
  * Client will reconnect to port returned by superserver
  * A client connected a port can communicate to another client connected to different port
 
### E2EE Encryption: RSA
  * E2EE encryption achieved using RSA which is a type of assymmetric encryption
  * Private Key stored locally in .pem files
  * Public keys ares stored in server DataBase under USER table
  * Messages are E2EE encrypted with 0% trust on server
  * Passwords are encrypted before sending to server
  
## Personal Chats:
  * A user can send message to any other user even if he is offline
  * Online user can receive message instantaneously through threading
  * Offline user can receive message as notifications when he/she logs in
 
### Group Chats:
  * Groups can be created by anyone
  * Group members can send message to everyone in a group
  * An online user can receive message from his/her group instantaneously through threading
  * An offline user can receive message from his/her group as notifications when he/she logs in
  
### Tester:
  * To test multiple servers and multiple clients to send messages with each other
  
## Partially Implemented
### Sending Images:
  * Images can be sent
  * Code is not merged with main code
 
### GUI: TKinter
  * Implemented a basic TKinter GUI for this chat app
  * Pending: Did not synchronise the work so far with TKinter
  * Issue: Not sure (as of now) whether we'll use this GUI in latter time

## Technology Used:
  * Python
  * PostgreSQL
  * RSA library
  * Socket programming
  * Threading
  * Selectors
  * Json
  * .pem files
  * Base64
 

## How to run:
* python3.10 db.py            // make sure postgreSQL is installed
* python3.10 chat_server.py
* python3.10 chat_client.py   // any number of clients
