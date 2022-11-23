import socket
import sys
import json
import rsa
import string 

def strToPublicKey(str):
    str = str[10:-1]
    li_temp = str.split(", ")
    to_public_key = rsa.PublicKey(n = int(li_temp[0]), e = int(li_temp[1]))
    return to_public_key


def encrypt(msg, key):
    return rsa.encrypt(msg.encode('ascii'), key)

def decrypt(ciphertext, key):
    c_list = ciphertext.split(' ')
    print(c_list)
    c_list = [eval(i) for i in c_list]
    ciphertext = bytes(c_list)
    try:
        return rsa.decrypt(ciphertext, key).decode('ascii')
    except:
        return False

def decryptAll(data, key):
    for p in data:
        print(type(p[0]))
        p[0] = decrypt(p[0], key)
    return data

host = "127.0.0.1"
port = 65432
server_address = (host,port)
usr_nam = ''
private_key = ""
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:          
    sock.connect(server_address)
except:
    print('Cannot connect to the server!') 
    sys.exit(1)   
try:
    while True:
        choice =input("Enter 1 to login OR Enter 2 to sign in: ")
        if choice == "1":
            user_name = input("Please enter your name: ")
            password = input("Please enter your password: ")
            info={"info-type":"login", "name":user_name,"password":password}       
            try:
                sock.sendall(json.dumps(info).encode())
            except:
                print('Cannot login currently! please try again later')
                sys.exit(1)
            is_succ = sock.recv(1024).decode()
            if(is_succ == "1"):
                usr_nam = user_name
                # try:
                with open("private_%s.pem"%user_name, "rb") as f:
                    private_key = rsa.PrivateKey.load_pkcs1(f.read())
                # except:
                    # print("Private Key Lost")
                    # exit()
                    
                print("login successfull!\n")
                break
            else:
                print("incorrect username!")
        elif choice == "2":
            name = input("Please enter your name: ")
            password = input("Please create a password: ")
            new_public_key, new_private_key = rsa.newkeys(1024)
            pkey = str(new_public_key)
            info = {"info-type":"signup", "name":name,"password":password, "public_key":pkey}
            try:
                sock.sendall(json.dumps(info).encode())
            except:
                print('Cannot sing up currently! please try again later')
                sys.exit(1)
            is_succ = sock.recv(1024).decode()
            if(is_succ == "1"):
                usr_nam = name
                with open('private_%s.pem'%name, "wb") as f:
                    f.write(new_private_key.save_pkcs1("PEM"))
                private_key = new_private_key
                print("successfully created an account\n")
                break
            else:
                print("Username already taken. please choose another username")
        else:
            continue

    while True:
        choice = input("Enter 1 to see list or 2 to see unread messages: ")
        if choice == "1":
            info = {"info-type":"online"}
            info = json.dumps(info)
            sock.send(info.encode())
            data = sock.recv(1024)
            data = data.decode()
            data = json.loads(data)   
            num = 0 
            p = []                      
            for pair in data["list"]:
                if not pair[0] == usr_nam.upper():
                    num+=1
                    print("{0}. {1}".format(num,pair[0]))
                else:
                    p = pair
            data["list"].remove(p)
            if(data["list"] == []):
                print("No one online currently")
                continue
            n = int(input("select user: "))
            print("selected {0}".format(data["list"][n-1][0]))

            to_public_key = strToPublicKey(data["list"][n-1][2])

            message = input("Enter a message: ")
            print(message)
            message = encrypt(message, to_public_key)
            print(message)
            # message = ' '.join(str(x) for x in message)
            # message = codecs.decode(message)
            byte_list = list(message)
            message = ' '.join(str(val) for val in byte_list)
            print(message)

            info = {"info-type":"message","text":message,"receiver":data["list"][n-1][1]}
            info = json.dumps(info)
            #print  ('%s: sending "%s"' % (sock.getsockname(), message))
            sock.send(info.encode())            
        elif choice == "2":            
            info = {"info-type":"unread"}
            info = json.dumps(info)
            sock.send(info.encode())
            data = sock.recv(10000)
            data = data.decode()
            print(data)
            data = json.loads(data)
            data = decryptAll(data["msgList"], private_key)
            print(data)            
        else:
            continue

except KeyboardInterrupt:    
    sock.close()        
