from anki.collection import _Collection
oldInit = _Collection.__init__

def newInit(self,*args,**kwargs):
    oldInit(self,*args,**kwargs)
    self.fixIntegrity()
#_Collection.__init__ = newInit
