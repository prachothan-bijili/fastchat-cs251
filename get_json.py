
def json_splitter(s):
    """
    | Splits multiple jsons so that we can process each one by one

    :param s: a string containing multiple jsons
    :type s: str
    :return: list of jsons
    :rtype: list

    """

    jsonlist = []
    count = 0
    current = 0
    for i in range(0,len(s)):
        if(s[i] == '{'):
            count+=1
        elif s[i] == '}':
            count -=1
            if(count == 0):
                jsonlist.append(s[current:i+1])
                current = i+1
    return jsonlist
