import os
paths = ["E://",'.', "C://", "D://", '/Users']
def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)
    
def readFile(NAME):
    ##This is for searching the entire computer
    # file = ''
    # for i in range (len(paths)):
    #     file = find(NAME, paths[i])
    #     if file != None:
    #         f = open(file)
    #         contents = f.readlines()
    #         return(contents)
    ##This is for if setup.txt is in the folder
    try:
        return(loadStrings(open(NAME)))
    except:
        return(None)
