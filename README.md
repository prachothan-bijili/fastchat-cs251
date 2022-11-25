# fastchat-cs251
## Team memebers 
  * Vinu Rakav S: MultiServer load balancing, improving throughput and latency, group chat and messaging, documentation
  * Prachothan Bijili: DataBase Processes, threading for simultaneous processes, bast tester, improving the throughput and latency, group creation, documentation
  * Tulsiram: E2EE Encryption, Image messaging, improving throughput and latency, load balancing strategy idealogies, documentation.


## Implemented So far:
### DataBase: PostgreSQL 
  * Consists of 4 tables
     * USERS
        * Consists of user details for each user
        * Password is encrypted before 
     * MSG -> All messages
     * GRP -> Details of group
     * GRP_MEMB -> Members of a group

### Multi-Client Multi-Server connection: SELECT and Threading
  * Multiple client multiple server implemented by using selectors and threading
  * Client will be connected to superserver(a port reserved for superserver) and superserver will return the port having minimum number of clients connected to this port
  * Client will reconnect to port returned by superserver
  * There are 5 servers connecting the superserver 
  * A client connected a port can communicate to another client connected to different port
  * Another Strategy implemented:
       1) Random Strategy, code files are submitted
       2) This doesn't have any super server, it randoms connects to server port out of 5 running servers
       3) if any server is down, other server will continue working
 
### E2EE Encryption: RSA
  * E2EE encryption achieved using RSA which is a type of assymmetric encryption
  * Private Key stored locally in .pem files
  * Public keys are stored in server DataBase under USER table
  * Messages are E2EE encrypted with 0% trust on server
  * Passwords are hashed before sending to the server, so that there is no possibility of password leackage through airing
  * Individiual and Group messages are both encrypted
  
## Personal Chats:
  * A user can send message to any other user even if he is offline
  * Online user can receive message instantaneously through threading
  * Offline user can receive message as notifications when he/she logs in
  * E2E Encryption is implemented for utmost security
 
### Group Chats:
  * Groups can be created by anyone
  * Group members can send message to everyone in a group
  * An online user can receive message from his/her group instantaneously through threading
  * An offline user can receive message from his/her group as notifications when he/she logs in
  * every message in the group is encrypted and is 100% safe
  
### Tester:
  * To test multiple servers and multiple clients to send messages with each other
  * atleast 100 users logging into and loggingout the server simultaneously with negligible intermediate time and any number of people being online
  * Least Connections Load Strategy is verified from this test
  * test is implemented For Random strategy and comparision is made:
      * Least Connection Load Strategy is better than random Strategy
      * When theoritically argued we can say that least Connection Strategy is better than Round Robin Strategy ehich is better than Random Strategy 
  
## Partially Implemented
### Sending Images:
  * Image is divided into multiple packages of same size
  * implemented the idea in the case of user being online/offline
  * Added the code files in the repository
  * Code is not merged with main code
  * The problem being: Few of the image packages are not being sent to server, but every package which is sent to server is ransferred to client without any problem
 
### GUI: TKinter
  * Implemented a basic TKinter GUI for this chat app
  * Pending: Did not synchronise the work so far with TKinter
  * Not continued this because of lack of time

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
* python3 db.py            // make sure postgreSQL is installed
* python3 chat_server.py
* python3 chat_client.py   // any number of clients
