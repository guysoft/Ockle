

import threading
 
class FuncThread(threading.Thread):
    '''
    A class to make functions threadable
    '''
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)
        return
 
    def run(self):
        self._target(*self._args)
        
        return

ID=0
THREAD=1

class workerEngine(object):
    ''' Control a class of worker functions threads
    '''
    def __init__(self):
        #list of worker threads
        self.workers=[]
        
    def getWorkers(self):
        return self.workers
      
    def addWorker(self,workerID,func):
        ''' Add a worker thread
        @param workerID: A unique string for the worker, usually the server name
        @param func: A function to work on
        @return: the thread, if needed
        '''
        t = FuncThread(func)
        self.workers.append((workerID,t))
        t.start()
        return t
    
    def isWorker(self,workerID):
        for worker in self.getWorkers():
            if worker[ID] == workerID:
                return True
        return False
    
    def cleanDoneWorkers(self):
        ''' Clears done workers and removes them from worker list
        '''
        for worker in self.getWorkers():
            if not worker[THREAD].isAlive():
                worker[THREAD].join()
                self.workers.remove(worker)
                        
    def waitForWorkers(self):
        ''' Wait for all workers to finish '''
        for worker in self.getWorkers():
            worker[THREAD].join()
        self.workers = []
    
    def getWorkerCount(self):
        return len(self.workers)