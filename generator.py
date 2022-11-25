import random

def generateID(table,cursor):    
    """
    | Generates unique ID for user or group based on user's request

    :param table: Generate ID for user or group
    :type table: str
    :param cursor: object that allows us to access postgresql database
    :type cursor: connection

    :return: unique ID
    :rtype: str

    """
    
    id = ''    
    while True:
        for i in range(7):
            r = random.choice([1, 2, 3])
            if r == 1:
                id += chr(random.randint(65, 90))
            elif r == 2:
                id += chr(random.randint(97, 122))
            else:
                id += str(random.randint(0,9))   
                
        cursor.execute('''select id from {0}'''. format(table))         
        l = cursor.fetchall()

        is_pre = False
        for i in l:
            if i[0] == id:
                is_pre = True
                break
        if is_pre:
            continue
        else:
            return id
