import rsa


def loadPrivateKey(usrname):
    """
    | loads the stored Private Key(in .pem file inside pems folder) whenever the user logins. This is must for the messages to be decrypted

    :param usrname: username of user for whom we require private key
    :type usrname: str

    :return: Private Key of that user
    :rtype: rsa.key.PrivateKey

    """
    try:
        private_key = 0
        with open("./pems/private_%s.pem"%usrname, "rb") as f:
            # print(f.read())
            private_key = rsa.PrivateKey.load_pkcs1(f.read())
            # print(private_key)
        return private_key
    except:
        return None

def storePrivateKey(usrname, prikey):
    """
    | stores the private key of user into a local directory (./pems) in a *.pem file so that it canbe extracted for further use. This is called whenever user signups for the first time

    :param usrname: username of user whose private key is being stored
    :type usrname: str
    :param prikey: private key of user which is to be stored
    :type prikey: rsa.key.PrivateKey

    """    
    with open('./pems/private_%s.pem'%usrname, "wb") as f:
        f.write(prikey.save_pkcs1("PEM"))

def strToPublicKey(str):
    """
    | Extracts Publickey from Public key string . server sends public key in the form of public key string only

    :param str: Public key string or string of the form "PublicKey(<PublicKey>)
    :type str: str

    :return: extracted Public key
    :rtype: rsa.key.PublicKey

    """
    str = str[10:-1]
    li_temp = str.split(", ")
    to_public_key = rsa.PublicKey(n = int(li_temp[0]), e = int(li_temp[1]))
    return to_public_key


def encrypt(msg, key):
    """
    | Encrypts the the given message with the given key string(which is PublicKey  string). Encrypts string to string.

    :param msg: Message which is to be encrypted
    :type msg: str
    :param key: Public key string which is used to encrypt the message
    :param key: str

    :return: encrypted message
    :rtype: str

    """
    pubkey = strToPublicKey(key)
    msg  = rsa.encrypt(msg.encode('ascii'), pubkey)
    byte_list = list(msg)
    msg = ' '.join(str(val) for val in byte_list)
    return msg

def decrypt(ciphertext, key):
    """
    | decrypts the given ciphertext(which is in string from of byte list) with the private key of user to return the actual message

    :param ciphertext: text which is to be decrypted
    :type ciphertext: str
    :param key: PrivateKey of the user which is used to decrypt the aired message
    :type key: rsa.key.PrivateKey

    :return: decrypted message
    :rtype: str

    """
    c_list = ciphertext.split(' ')
    c_list = [eval(i) for i in c_list]
    ciphertext = bytes(c_list)
    try:
        return rsa.decrypt(ciphertext, key).decode('ascii')
    except:
        return False
