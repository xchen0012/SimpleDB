import sys
class WrongCommandException(Exception):
    def __init__(self,string):
        print string
class myDB(object):

    def __init__(self):
        self.persistDict = {} # commit version,stroing persistent data, Only one exist in mydb
        self.tempDict = {}# stroing transaction data,contains multiple transaction temp dictionary
        self.cache={}# improve get time,Only one exist in mydb
        #deleteKey = {}# store delete keys
        self.numDict ={}# map(value,number of value),Only one exist in mydb
        self.transaction =0

    def get(self, key):
            #used a cache to improve search time
        if key in self.cache:    
            return self.cache[key] 
        # if not in cache, find it in temp dictionary 
        if self.transaction >0:
            for version in xrange(self.transaction,0,-1):
                if key in self.tempDict[version]:
                    value = self.tempDict[version][key]
                    
                    self.cache[key]=value
                    return value    
        # if not in temp dictionary, check it in persistance dictionary      
        if key in self.persistDict:
            value = self.persistDict[key]
            self.cache[key] =value
            return value
        return 'NULL'
    def rollback(self):
        if self.transaction>0:
            self.transaction-=1 #go back to last temp dictionary and delete key set
            for key in list(self.tempDict[self.transaction+1]):
                if self.tempDict[self.transaction+1][key]!='NULL':
                    self.numDict[self.tempDict[self.transaction+1][key]]-=1 # since rollback, undo what transaction did
                self.tryDel(self.tempDict[self.transaction+1],key) 
                self.tryDel(self.cache,key)# since value maybe changed in cache, should delete it
                v = self.get(key)
                if v !='NULL':
                    self.numDict[v]+=1 # update number in numDict
            del self.tempDict[self.transaction+1]
                        
        else:
            print 'NO TRANSACTION'
    def commit(self):
        if self.transaction >0:
            for version in xrange(1,self.transaction+1): # flush temp dictionary from oldest to newest
                for key in self.tempDict[version]:
                    self.persistDict[key] = self.tempDict[version][key]
                            #for key in deleteKey[version]:
                             #   tryDel(persistDict,args[1])
                                
            self.transaction=0
    def unset(self,key):
        value = self.get(key)
        if value!='NULL':
            self.numDict[self.get(key)]-=1
        if self.transaction >0:
            self.tempDict[self.transaction][key]='NULL'
          #  deleteKey[transaction].add(args[1])
        else:
            self.tryDel(self.persistDict,key)
        self.cache[key]='NULL'
    def numequalto(self,value):
        if value in self.numDict:
            print self.numDict[value]
        else:
            print 0
    def set(self,key,value):
        if value not in self.numDict:
            self.numDict[value]=0
        self.numDict[value]+=1
        v = self.get(key)
        if v!='NULL':
            self.numDict[v]-=1
        self.cache[key]=value#since new value update, cache should update
        # check wether in a transaction
        if self.transaction>0:
            self.tempDict[self.transaction][key]=value
        else:
            self.persistDict[key]=value
    def transactionBegin(self):
        self.transaction+=1
        self.tempDict[self.transaction]={} #Initial temp Transaction Dictionary
    def end(self):
        del self.persistDict
        del self.tempDict
        del self.numDict
        del self.cache

    def tryDel(self,mydict, key):
        try:
            del mydict[key]
        except KeyError:
            pass

    def start(self):
        
        while True:
            try:
                line = sys.stdin.readline()
                line = line.lower().strip()
                args = line.split()
                if len(args)==1:
                    # END COMMAND
                    if line == 'end':
                        self.end()
                        break
                    # TRANSACTION COMMAND
                    elif line == 'begin':
                        self.transactionBegin()
                    # ROLLBACK COMMAND
                    elif line == 'rollback':
                        self.rollback()
                    # COMMIT COMMAND
                    elif line == 'commit':   
                        self.commit()
                    else:
                        raise WrongCommandException('could not find command: \'%s\''%line)

                elif len(args)==2:
                    # GET COMMAND
                    if args[0] == 'get':
                        value=self.get(args[1])
                        print value
                    # UNSET COMMAND
                    elif args[0] == 'unset':
                        self.unset(args[1])
                    #NUMEQUALTO COMMAND
                    elif args[0] == 'numequalto':
                        self.numequalto(args[1])
                    else:
                        raise WrongCommandException('could not find command: \'%s\''%line)

                elif len(args)==3:
                    #SET COMMAND
                    if args[0] == 'set':
                        self.set(args[1],args[2])
                        
                    else:
                        raise WrongCommandException('could not find command: \'%s\''%line)
                else:
                    raise WrongCommandException('could not find command: \'%s\''%line)
            except WrongCommandException:
                pass

if __name__ == '__main__':
    #global transaction   
    db = myDB()
    db.start()

