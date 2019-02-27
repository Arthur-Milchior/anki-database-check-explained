from .check import basicCheck
from aqt import mw
from anki.hooks import addHook
from anki.collection import _Collection
oldInit = _Collection.__init__

def newInit(self,*args,**kwargs):
    oldInit(self,*args,**kwargs)
    self.basicCheck()
_Collection.__init__ = newInit
