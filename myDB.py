import sys
def get(transaction, key,allowPrint=True):
    #used a cache to improve search time
    if key in cache:
        if allowPrint:
            print cache[key]
        return cache[key] 
    # if not in cache, find it in temp dictionary 
    if transaction >0:
        for version in xrange(transaction,0,-1):
            if key in tempDict[version]:
                value = tempDict[version][key]
                if allowPrint:
                    print value
                cache[key]=value
                return value    
    # if not in temp dictionary, check it in persistance dictionary      
    if key in persistDict:
        value = persistDict[key]
        cache[key] =value
        if allowPrint:
            print value
        return value
    else:
        if allowPrint:
            print 'NULL'
        return 'NULL'

def tryDel(mydict, key):
    try:
        del mydict[key]
    except KeyError:
        pass

def myDB():
    transaction = 0
    while True:
        line = sys.stdin.readline()
        line = line.lower().strip()
        args = line.split()

        if len(args)==1:
            # END COMMAND
            if line == 'end':
                break
            # TRANSACTION COMMAND
            elif line == 'begin':
                transaction+=1
                tempDict[transaction]={} #Initial temp Transaction Dictionary
            # ROLLBACK COMMAND
            elif line == 'rollback':
                if transaction>0:
                    transaction-=1 #go back to last temp dictionary and delete key set
                    for key in list(tempDict[transaction+1]):
                        if tempDict[transaction+1][key]!='NULL':
                            numDict[tempDict[transaction+1][key]]-=1 # since rollback, undo what transaction did
                        tryDel(tempDict[transaction+1],key) 
                        tryDel(cache,key)# since value maybe changed in cache, should delete it
                        v = get(transaction,key,False)
                        if v !='NULL':
                            numDict[v]+=1 # update number in numDict
                    del tempDict[transaction+1]
                    
                else:
                    print 'NO TRANSACTION'
            # COMMIT COMMAND
            elif line == 'commit':   
                if transaction >0:
                    for version in xrange(1,transaction+1): # flush temp dictionary from oldest to newest
                        for key in tempDict[version]:
                            persistDict[key] = tempDict[version][key]
                        #for key in deleteKey[version]:
                         #   tryDel(persistDict,args[1])
                            
                    transaction=0
            else:
                print 'could not find command: \'%s\''%line

        elif len(args)==2:
            # GET COMMAND
            if args[0] == 'get':
                get(transaction,args[1])
            # UNSET COMMAND
            elif args[0] == 'unset':
                numDict[get(transaction,args[1],False)]-=1
                if transaction >0:
                    tempDict[transaction][args[1]]='NULL'
                  #  deleteKey[transaction].add(args[1])
                else:
                    tryDel(persistDict,args[1])
                cache[args[1]]='NULL'
            #NUMEQUALTO COMMAND
            elif args[0] == 'numequalto':
                if args[1] in numDict:
                    print numDict[args[1]]
                else:
                    print 0
            else:
                print 'could not find command: \'%s\''%line

        elif len(args)==3:
            #SET COMMAND
            if args[0] == 'set':
                if args[2] not in numDict:
                    numDict[args[2]]=0
                numDict[args[2]]+=1
                v = get(transaction,args[1],False)
                if v!='NULL':
                    numDict[v]-=1
                cache[args[1]]=args[2]#since new value update, cache should update
                # check wether in a transaction
                if transaction>0:
                    tempDict[transaction][args[1]]=args[2]
                else:
                    persistDict[args[1]]=args[2]
            
        else:
            print 'could not find command: \'%s\''%line
if __name__ == '__main__':
    #global transaction
    persistDict = {} # commit version,stroing persistent data, Only one exist in mydb
    tempDict = {}# stroing transaction data,contains multiple transaction temp dictionary
    cache={}# improve get time,Only one exist in mydb
    #deleteKey = {}# store delete keys
    numDict ={}# map(value,number of value),Only one exist in mydb
    myDB()

