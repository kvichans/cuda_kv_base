import unittest

import os, tempfile
from cuda_kv_base import get_hist, set_hist

class TestSetHist(unittest.TestCase):
    def fd(self):  return open(self.fn).read().replace(chr(10),'').replace(' ','')
    def __init__(self, methodName='runTest'):
        super().__init__(methodName)

        with tempfile.NamedTemporaryFile() as fp:
            self.fn = fp.name+'.json'
        pass;                  #print('.fn=',self.fn)
        self.env     = dict(                    kill=False, to_file=self.fn)        
        self.envM    = dict(module_name='mymo', kill=False, to_file=self.fn)
        self.envMF   = dict(module_name='mymo'            , to_file=self.fn)
        self.envF    = dict(                                to_file=self.fn)

    def test_set_hist_empty(self):
        """ If old state is empty
             set_hist('k',0,None)                                                {"k":0}
             set_hist('k',1)                                                     {"mymo":{"k":1}}
             set_hist('k',1,'mymo')                                              {"mymo":{"k":1}}
             set_hist('k',1,'oth')                                               {"oth":{"k":1}}
             set_hist('k',[1,2])                                                 {"mymo":{"k":[1,2]}}
             set_hist(['p','k'], 1)                                              {"mymo":{"p":{"k":1}}}
        """
        def cf():  os.remove(self.fn) if os.path.exists(self.fn) else 0
        cf();set_hist('k',0,None    ,**self.env);   self.assertEqual(self.fd(), '{"k":0}')
        cf();set_hist('k',1,'mymo'  ,**self.env);   self.assertEqual(self.fd(), '{"mymo":{"k":1}}')
        cf();set_hist('k',1         ,**self.envM);  self.assertEqual(self.fd(), '{"mymo":{"k":1}}')
        cf();set_hist('k',1,'oth'   ,**self.env);   self.assertEqual(self.fd(), '{"oth":{"k":1}}')
        cf();set_hist('k',[1,2]     ,**self.envM);  self.assertEqual(self.fd(), '{"mymo":{"k":[1,2]}}')
        cf();set_hist(['p','k'], 1  ,**self.envM);  self.assertEqual(self.fd(), '{"mymo":{"p":{"k":1}}}')

    def test_set_hist_filled(self):
        """ If old state is                                                      {"mymo":{"k":1,"p":{"m":2}}}
                                                it will contain
            set_hist('k',0,None)                                                 {"mymo":{"k":1,"p":{"m":2}},"k":0}
            set_hist('k',0)                                                      {"mymo":{"k":0,"p":{"m":2}}}
            set_hist('k',0,'mymo')                                               {"mymo":{"k":0,"p":{"m":2}}}
            set_hist('n',3)                                                      {"mymo":{"k":1,"p":{"m":2},"n":3}}
            set_hist(['p','m'], 4)                                               {"mymo":{"k":1,"p":{"m":4}}}
            set_hist('p',{'m':4})                                                {"mymo":{"k":1,"p":{"m":4}}}
            set_hist(['p','m','k'], 1)          KeyError (old m is not branch node)
        """
        start_cont  =                                                           '{"mymo":{"k":1,"p":{"m":2}}}'
        def ff():  open(self.fn,'w').write(start_cont)
        ff();set_hist('k',0,None    ,**self.env);   self.assertEqual(self.fd(), '{"mymo":{"k":1,"p":{"m":2}},"k":0}')
        ff();set_hist('k',0         ,**self.envM);  self.assertEqual(self.fd(), '{"mymo":{"k":0,"p":{"m":2}}}')
        ff();set_hist('k',0,'mymo'  ,**self.env);   self.assertEqual(self.fd(), '{"mymo":{"k":0,"p":{"m":2}}}')
        ff();set_hist('n',3         ,**self.envM);  self.assertEqual(self.fd(), '{"mymo":{"k":1,"p":{"m":2},"n":3}}')
        ff();set_hist(['p','m'], 4  ,**self.envM);  self.assertEqual(self.fd(), '{"mymo":{"k":1,"p":{"m":4}}}')
        ff();set_hist('p',{'m':4}   ,**self.envM);  self.assertEqual(self.fd(), '{"mymo":{"k":1,"p":{"m":4}}}')
        ff();
        with self.assertRaises(KeyError):
            set_hist(['p','m','k'], 1,**self.envM)
        ff();
    
    def test_set_hist_kill(self):
        """ If old state is                                                         {"mymo":{"k":1,"p":{"m":2}}}
                                                it will contain
            set_hist('k',       kill=True)                                          {"mymo":{"p":{"m":2}}}
            set_hist('p',       kill=True)                                          {"mymo":{"k":1}}
            set_hist(['p','m'], kill=True)                                          {"mymo":{"k":1,"p":{}}}
            set_hist('n',       kill=True)                                          {"mymo":{"k":1,"p":{"m":2}}}    (nothing to kill)
        """
        start_cont  =                                                              '{"mymo":{"k":1,"p":{"m":2}}}'
        def ff():  open(self.fn,'w').write(start_cont)
        ff();set_hist('k',kill=True      ,**self.envMF);self.assertEqual(self.fd(),'{"mymo":{"p":{"m":2}}}')
        ff();set_hist('p',kill=True      ,**self.envMF);self.assertEqual(self.fd(),'{"mymo":{"k":1}}')
        ff();set_hist(['p','m'],kill=True,**self.envMF);self.assertEqual(self.fd(),'{"mymo":{"k":1,"p":{}}}')
        ff();set_hist('n',kill=True      ,**self.envMF);self.assertEqual(self.fd(),'{"mymo":{"k":1,"p":{"m":2}}}')

    def test_get_hist_empty(self):
        """
        If old state is empty
                            get_hist('k')                   returns None
                            get_hist(['p', 'k'], 0)         returns 0
        """
        os.remove(self.fn) if os.path.exists(self.fn) else 0
        self.assertEqual(   get_hist('k'            ,**self.envMF) ,None)
        self.assertEqual(   get_hist(['p', 'k'], 0  ,**self.envMF) ,0)

    def test_get_hist_filled(self):
        """
        If state is              {"k":1, "mymo":{"k":2, "p":{"m":3}, "t":[0,1]}, "q":{"n":4}}
                            get_hist('k', 0, None)              returns 1
                            get_hist('k', 0)                    returns 2
                            get_hist('k', 0, 'mymo')            returns 2
                            get_hist('k', 0, 'oth')             returns 0
                            get_hist(['p','m'], 0)              returns 3
                            get_hist(['t'], [])                 returns [0,1]
                            get_hist('q', 0, None)              returns {'n':4}
                            get_hist(['q','n'], 0, None)        returns 4
        """
        open(self.fn,'w').write('{"k":1, "mymo":{"k":2, "p":{"m":3}, "t":[0,1]}, "q":{"n":4}}')
        self.assertEqual(   get_hist('k', 0, None       ,**self.envF)  ,1)
        self.assertEqual(   get_hist('k', 0             ,**self.envMF) ,2)
        self.assertEqual(   get_hist('k', 0, 'mymo'     ,**self.envF)  ,2)
        self.assertEqual(   get_hist('k', 0, 'oth'      ,**self.envF)  ,0)
        self.assertEqual(   get_hist(['p','m'], 0       ,**self.envMF) ,3)
        self.assertEqual(   get_hist(['t'], []          ,**self.envMF) ,[0,1])
        self.assertEqual(   get_hist('q', 0, None       ,**self.envF)  ,{'n':4})
        self.assertEqual(   get_hist(['q','n'], 0, None ,**self.envF)  ,4)
