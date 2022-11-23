# fastchat-cs251
Team memebers --> Vinu, Prachothan, Tulsiram


## Implemented So far:
### DataBase: PostgreSQL 
  * Consists of 4 tables
  * Explained in Presentation

### Multi-Client Server connection: SELECT
  * Multiple client single server implemented by using selectors
 
### E2EE Encryption: RSA
  * E2EE encryption achieved using RSA which is a type of assymmetric encryption
  * Private Key stored locally in .pem files
  * Public keys ares stored in server DataBase under USER table
  * Messages are E2EE encrypted with 0% trust on server
 
### Sending Images:
  * Images can be sent
  * Code is not merged with main code
 
## Partially implemented:
### Group Chats:
  * Creation of Groups is done
  * Creation of tables in DataBase is also completed
  * Pending: Combining Tables to get final output
 
### GUI: TKinter
  * Implemented a basic TKinter GUI for this chat app
  * Pending: Did not synchronise the work so far with TKinter
  * Issue: Not sure (as of now) whether we'll use this GUI in latter time
 
## Yet To be Done:
### Multiple-Client Multiple-Servers
  * Discussed the strategy to manage Multiple-servers
  * Tried Implemented Multiple Servers using 'Random' Load Balancing strategy - faced Bugs
  * To be done

###


## Technology Used:
  * PostgreSQL
  * RSA library
  * Socket programming
  * Selectors
  * Json
  * .pem files
  * Base64
 
## contribution:
  * Tulsi Ram
  * Prachothan
  * Vinu
