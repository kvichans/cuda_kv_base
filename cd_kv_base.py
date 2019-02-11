''' Lib for Plugin
Authors:
    Andrey Kvichansky    (kvichans on github.com)
Version:
    '0.8.01 2019-02-15'
Content
    log                 Logger with timing
    _                   i18n
    (g|s)et_hist        Read|write from|to "*.json" a value by string key or path
ToDo: (see end of file)
'''

import  sys, os, gettext, logging, inspect, time, collections, json, re, subprocess
from    time        import perf_counter

import  cudatext            as app
from    cudatext        import ed
import  cudax_lib           as apx

pass;                           # Logging
pass;                           from pprint import pformat
pass;                           import tempfile

odict       = collections.OrderedDict
T,F,N       = True, False, None
c13,c10,c9  = chr(13),chr(10),chr(9)

def f(s, *args, **kwargs):return s.format(*args, **kwargs)

#########################
#NOTE: log utility
#########################
def log(msg='', *args, **kwargs):
    """ Use params args and kwargs to substitute {} in msg.
        Output msg to current/new Tr. 
        Simple usage:  
                log('a={}', 1)
            output
                [12.34"]fn:123 a=1
            where 
                [12.34"]    Time from start of logging
                fn          Name of unit where log was called
                123         Line number  where log was called
        More:
            log('###')  # Output stack info
            log('¬¶')   # Output chr(9) and chr(10) characters
    """
    if args or kwargs:
        msg = msg.format(*args, **kwargs)
    if Tr.tr is None:
        Tr.tr=Tr()
    return Tr.tr.log(msg)
    
class Tr :
    """ Logger.
        Usage:
            t = Tr()        # log as print
            t = Tr(path)    # log to the file
            t.log(sdata)    # output the sdata.
        """
    to_file=None
    tr=None

    sec_digs        = 2                     # Digits in mantissa of second 
    se_fmt          = ''
    mise_fmt        = ''
    homise_fmt      = ''
    def __init__(self, log_to_file=None):
        log_to_file = log_to_file if log_to_file else Tr.to_file
        # Fields
        self.tm     = perf_counter()        # Start tick for whole log

        if log_to_file:
            logging.basicConfig( filename=log_to_file
                                ,filemode='w'
                                ,level=logging.DEBUG
                                ,format='%(message)s'
                                ,datefmt='%H:%M:%S'
                                ,style='%')
        else: # to stdout
            logging.basicConfig( stream=sys.stdout
                                ,level=logging.DEBUG
                                ,format='%(message)s'
                                ,datefmt='%H:%M:%S'
                                ,style='%')
    def log(self, msg='') :
        logging.debug( self.format_msg(msg) )
        return self 
        # Tr.log
            
    def format_msg(self, msg, dpth=3, ops='+fun:ln'):
        if '###' in msg :
            # Output stack
            st_inf  = '\n###'
            for fr in inspect.stack()[1+dpth:]:
                try:
                    cls = fr[0].f_locals['self'].__class__.__name__ + '.'
                except:
                    cls = ''
                fun     = (cls + fr[3]).replace('.__init__','()')
                ln      = fr[2]
                st_inf  += '    {}:{}'.format(fun, ln)
            msg    += st_inf

        if '+fun:ln' in ops :
            frCaller= inspect.stack()[dpth] # 0-format_msg, 1-Tr.log|Tr.TrLiver, 2-log, 3-need func
            try:
                cls = frCaller[0].f_locals['self'].__class__.__name__ + '.'
            except:
                cls = ''
            fun     = (cls + frCaller[3]).replace('.__init__','()')
            ln      = frCaller[2]
            msg     = '[{}]{}:{} '.format( Tr.format_tm( perf_counter() - self.tm ), fun, ln ) + msg
        else : 
            msg     = '[{}] '.format( Tr.format_tm( perf_counter() - self.tm ) ) + msg

        return msg.replace('¬',c9).replace('¶',c10)
        # Tr.format

    @staticmethod
    def format_tm(secs) :
        """ Convert secs to 12h34'56.78" """
        if 0==len(Tr.se_fmt) :
            Tr.se_fmt       = '{:'+str(3+Tr.sec_digs)+'.'+str(Tr.sec_digs)+'f}"'
            Tr.mise_fmt     = "{:2d}'"+Tr.se_fmt
            Tr.homise_fmt   = "{:2d}h"+Tr.mise_fmt
        h = int( secs / 3600 )
        secs = secs % 3600
        m = int( secs / 60 )
        s = secs % 60
        return Tr.se_fmt.format(s) \
                if 0==h+m else \
               Tr.mise_fmt.format(m,s) \
                if 0==h else \
               Tr.homise_fmt.format(h,m,s)
        # Tr.format_tm
    # Tr

#########################
#NOTE: misc for OS 
#########################

def get_translation(plug_file):
    ''' Part of i18n.
        Full i18n-cycle:
        1. All GUI-string in code are used in form 
            _('')
        2. These string are extracted from code to 
            lang/messages.pot
           with run
            python.exe <pypython-root>\Tools\i18n\pygettext.py -p lang <plugin>.py
        3. Poedit (or same program) create 
            <module>\lang\ru_RU\LC_MESSAGES\<module>.po
           from (cmd "Update from POT") 
            lang/messages.pot
           It allows to translate all "strings"
           It creates (cmd "Save")
            <module>\lang\ru_RU\LC_MESSAGES\<module>.mo
        4. get_translation uses the file to realize
            _('')
    '''
    plug_dir= os.path.dirname(plug_file)
    plug_mod= os.path.basename(plug_dir)
    lng     = app.app_proc(app.PROC_GET_LANG, '')
    lng_mo  = plug_dir+'/lang/{}/LC_MESSAGES/{}.mo'.format(lng, plug_mod)
    if os.path.isfile(lng_mo):
        t   = gettext.translation(plug_mod, plug_dir+'/lang', languages=[lng])
        _   = t.gettext
        t.install()
    else:
        _   =  lambda x: x
    return _
   #def get_translation

#_   = get_translation(__file__) # I18N

def get_desktop_environment():
    #From http://stackoverflow.com/questions/2035657/what-is-my-current-desktop-environment
    # and http://ubuntuforums.org/showthread.php?t=652320
    # and http://ubuntuforums.org/showthread.php?t=652320
    # and http://ubuntuforums.org/showthread.php?t=1139057
    if sys.platform in ["win32", "cygwin"]:
        return "win"
    elif sys.platform == "darwin":
        return "mac"
    else: #Most likely either a POSIX system or something not much common
        def is_running(process):
            #From http://www.bloggerpolis.com/2011/05/how-to-check-if-a-process-is-running-using-python/
            # and http://richarddingwall.name/2009/06/18/windows-equivalents-of-ps-and-kill-commands/
            try: #Linux/Unix
                s = subprocess.Popen(["ps", "axw"],stdout=subprocess.PIPE)
            except: #Windows
                s = subprocess.Popen(["tasklist", "/v"],stdout=subprocess.PIPE)
            for x in s.stdout:
                if re.search(process, str(x)):
                    return True
            return False

        desktop_session = os.environ.get("DESKTOP_SESSION")
        if desktop_session is not None: #easier to match if we doesn't have  to deal with caracter cases
            desktop_session = desktop_session.lower()
            if desktop_session in ["gnome","unity", "cinnamon", "mate", "xfce4", "lxde", "fluxbox", 
                                   "blackbox", "openbox", "icewm", "jwm", "afterstep","trinity", "kde"]:
                return desktop_session
            ## Special cases ##
            # Canonical sets $DESKTOP_SESSION to Lubuntu rather than LXDE if using LXDE.
            # There is no guarantee that they will not do the same with the other desktop environments.
            elif "xfce" in desktop_session or desktop_session.startswith("xubuntu"):
                return "xfce4"
            elif desktop_session.startswith("ubuntu"):
                return "unity"       
            elif desktop_session.startswith("lubuntu"):
                return "lxde" 
            elif desktop_session.startswith("kubuntu"): 
                return "kde" 
            elif desktop_session.startswith("razor"): # e.g. razorkwin
                return "razor-qt"
            elif desktop_session.startswith("wmaker"): # e.g. wmaker-common
                return "windowmaker"
        if os.environ.get('KDE_FULL_SESSION') == 'true':
            return "kde"
        elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
            if not "deprecated" in os.environ.get('GNOME_DESKTOP_SESSION_ID'):
                return "gnome2"
        #From http://ubuntuforums.org/showthread.php?t=652320
        elif is_running("xfce-mcs-manage"):
            return "xfce4"
        elif is_running("ksmserver"):
            return "kde"
    return "unknown"


#########################
#NOTE: cudatext helpers
#########################
def ed_of_file_open(op_file):
    if not app.file_open(op_file):
        return None
    for h in app.ed_handles(): 
        op_ed   = app.Editor(h)
        if op_ed.get_filename() and os.path.samefile(op_file, op_ed.get_filename()):
            return op_ed
    return None
   #def ed_of_file_open

def get_hotkeys_desc(cmd_id, ext_id=None, keys_js=None, def_ans=''):
    """ Read one or two hotkeys for command 
            cmd_id [+ext_id]
        from 
            settings\keys.json
        Return 
            def_ans                     If no  hotkeys for the command
            'Ctrl+Q'            
            'Ctrl+Q * Ctrl+W'           If one hotkey  for the command
            'Ctrl+Q/Ctrl+T'            
            'Ctrl+Q * Ctrl+W/Ctrl+T'    If two hotkeys for the command
    """
    if keys_js is None:
        keys_json   = app.app_path(app.APP_DIR_SETTINGS)+os.sep+'keys.json'
        keys_js     = apx._json_loads(open(keys_json).read()) if os.path.exists(keys_json) else {}

    cmd_id  = f('{},{}', cmd_id, ext_id) if ext_id else cmd_id
    if cmd_id not in keys_js:
        return def_ans
    cmd_keys= keys_js[cmd_id]
    desc    = '/'.join([' * '.join(cmd_keys.get('s1', []))
                       ,' * '.join(cmd_keys.get('s2', []))
                       ]).strip('/')
    return desc
   #def get_hotkeys_desc

######################################
#NOTE: plugins history
######################################
PLING_HISTORY_JSON  = app.app_path(app.APP_DIR_SETTINGS)+os.sep+'plugin history.json'
def get_hist(key_or_path, default=None, module_name='_auto_detect', to_file=PLING_HISTORY_JSON):
    """ Read from "plugin history.json" one value by string key or path (list of keys).
        Parameters
            key_or_path     Key(s) to navigate in json tree
                            Type: str or [str]
            default         Value to return  if no suitable node in json tree
            module_name     Start node to navigate.
                            If it is '_auto_detect' then name of caller module is used.
                            If it is None then it is skipped.
            to_file         Name of file to read. APP_DIR_SETTING will be joined if no full path.
        
        Return              Found value or default
            
        Examples (caller module is 'plg')
        1. If no "plugin history.json"
                get_hist('k')                   returns None
                get_hist(['p', 'k'], 0)         returns 0
        2. If "plugin history.json" contains 
                {"k":1, "plg":{"k":2, "p":{"m":3}, "t":[0,1]}, "q":{"n":4}}
                get_hist('k', 0, None)          returns 1
                get_hist('k', 0)                returns 0
                get_hist('k', 0, 'plg')         returns 2
                get_hist('k', 0, 'oth')         returns 0
                get_hist(['p','m'], 0)          returns 3
                get_hist(['p','t'], [])         returns [0,1]
                get_hist('q', 0, None)          returns {'n':4}
                get_hist(['q','n'], 0, None)    returns 4
    """
    to_file = to_file   if os.sep in to_file else   app.app_path(app.APP_DIR_SETTINGS)+os.sep+to_file
    if not os.path.exists(to_file):
        pass;                  #log('not exists',())
        return default
    data    = None
    try:
        data    = json.loads(open(to_file).read())
    except:
        pass;                   log('not load: {}',sys.exc_info())
        return default
    if module_name=='_auto_detect':
        caller_globals  = inspect.stack()[1].frame.f_globals
        module_name = inspect.getmodulename(caller_globals['__file__']) \
                        if '__file__' in caller_globals else None
    keys    = [key_or_path] if type(key_or_path)==str   else key_or_path
    keys    = keys          if module_name is None      else [module_name]+keys
    parents,\
    key     = keys[:-1], keys[-1]
    for parent in parents:
        data= data.get(parent)
        if type(data)!=dict:
            pass;               log('not dict parent={}',(parent))
            return default
    return data.get(key, default)
   #def get_hist

def set_hist(key_or_path, value, module_name='_auto_detect', kill=False, to_file=PLING_HISTORY_JSON):
    """ Write to "plugin history.json" one value by key or path (list of keys).
        If any of node doesnot exist it will be added.
        Or remove (if kill) one key+value pair (if suitable key exists).
        Parameters
            key_or_path     Key(s) to navigate in json tree
                            Type: str or [str]
            value           Value to set if suitable item in json tree exists
            module_name     Start node to navigate.
                            If it is '_auto_detect' then name of caller module is used.
                            If it is None then it is skipped.
            kill            Need to remove node in tree.
                            if kill==True parm value is ignored
            to_file         Name of file to write. APP_DIR_SETTING will be joined if no full path.
        
        Return              value (param)   if !kill and modification is successful
                            value (killed)  if  kill and modification is successful
                            None            if  kill and no path in tree (no changes)
                            KeyError        if !kill and path has problem
        Return  value
            
        Examples (caller module is 'plg')
        1. If no "plugin history.json"  it will become
            set_hist('k',0,None)        {"k":0}
            set_hist('k',1)             {"plg":{"k":1}}
            set_hist('k',1,'plg')       {"plg":{"k":1}}
            set_hist('k',1,'oth')       {"oth":{"k":1}}
            set_hist('k',[1,2])         {"plg":{"k":[1,2]}}
            set_hist(['p','k'], 1)      {"plg":{"p":{"k":1}}}
        
        2. If "plugin history.json" contains    {"plg":{"k":1, "p":{"m":2}}}
                                                it will contain
            set_hist('k',0,None)                {"plg":{"k":1, "p":{"m":2}},"k":0}
            set_hist('k',0)                     {"plg":{"k":0, "p":{"m":2}}}
            set_hist('k',0,'plg')               {"plg":{"k":0, "p":{"m":2}}}
            set_hist('n',3)                     {"plg":{"k":1, "p":{"m":2}, "n":3}}
            set_hist(['p','m'], 4)              {"plg":{"k":1, "p":{"m":4}}}
            set_hist('p',{'m':4})               {"plg":{"k":1, "p":{"m":4}}}
            set_hist(['p','m','k'], 1)          KeyError (old m is not branch node)

        3. If "plugin history.json" contains    {"plg":{"k":1, "p":{"m":2}}}
                                                it will contain
            set_hist('k',       kill=True)      {"plg":{       "p":{"m":2}}}
            set_hist('p',       kill=True)      {"plg":{"k":1}}
            set_hist(['p','m'], kill=True)      {"plg":{"k":1, "p":{}}}
            set_hist('n',       kill=True)      {"plg":{"k":1, "p":{"m":2}}}    (nothing to kill)
    """
    to_file = to_file   if os.sep in to_file else   app.app_path(app.APP_DIR_SETTINGS)+os.sep+to_file
    body    = json.loads(open(to_file).read(), object_pairs_hook=odict) \
                if os.path.exists(to_file) and os.path.getsize(to_file) != 0 else \
              odict()

    if module_name=='_auto_detect':
        caller_globals  = inspect.stack()[1].frame.f_globals
        module_name = inspect.getmodulename(caller_globals['__file__']) \
                        if '__file__' in caller_globals else None
    keys    = [key_or_path] if type(key_or_path)==str   else key_or_path
    keys    = keys          if module_name is None      else [module_name]+keys
    parents,\
    key     = keys[:-1], keys[-1]
    data    = body
    for parent in parents:
        if kill and parent not in data:
            return None
        data= data.setdefault(parent, odict())
        if type(data)!=odict:
            raise KeyError()
    if kill:
        if key not in data:
            return None
        value       = data.pop(key)
    else:
        data[key]   =  value
    open(to_file, 'w').write(json.dumps(body, indent=2))
    return value
   #def set_hist


######################################
#NOTE: misc for pyhthon
######################################
def set_all_for_tree(tree, sub_key, key, val):
    for node in tree:
        if sub_key in node:
            set_all_for_tree(node[sub_key], sub_key, key, val)
        else:
            node[key]   = val
   #def set_all_for_tree

def upd_dict(d1, d2):
    rsp = d1.copy()
    rsp.update(d2)
    return rsp
   #def upd_dict

def deep_upd(dcts):
    pass;                      #log('dcts={}',(dcts))
    if not dcts:
        return dcts
    if isinstance(dcts, dict):
        return dcts

    dct1, *dcts = dcts
    pass;                      #log('dct1, dcts={}',(dct1, dcts))
    rsp   = dct1.copy()
    for dct in dcts:
        for k,v in dct.items():
            if False:pass
            elif k not in rsp:
                rsp[k]  = v
            elif isinstance(rsp[k], dict) and isinstance(v, dict):
                rsp[k].update(v)
            else:
                rsp[k]  = v
    pass;                      #log('rsp={}',(rsp))
    return rsp
   #def deep_upd

def isint(what):    return isinstance(what, int)
   
if __name__ == '__main__' :
    # To start the tests run in Console
    #   exec(open(path_to_the_file, encoding="UTF-8").read())
    print('Start tests')
    log('a={}',1.23)
    print('Stop tests')
'''
ToDo
[+][kv-kv][11feb19] Extract from cd_plug_lib.py
[ ][kv-kv][11feb19] Set tests
'''
