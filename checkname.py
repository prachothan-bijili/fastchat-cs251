
def checkname(name,password,is_log,cursor):          
    """
    | Searches if user already exists and returns True if found else False

    :param name: name of user
    :type name: str
    :param password: password of user
    :type password: str
    :param is_log: login or signup
    :type is_log: bool
    :param cursor: object that allows us to access postgresql database
    :type cursor: connection

    :return: True if user is found, False if not found
    :rtype: bool
    """
    cursor.execute('''select name,password from USERS ''')    
    l = cursor.fetchall()
    for pair in l:
        if pair[0] == name.upper():
            if (not is_log) or pair[1] == password:
                return True
            else:
                break
    return False