Library for logging, i18n, storing plugin options/states and so on.

Author: Andrey Kvichansky    (kvichans on github.com)
License: MIT

Library contents:

============
1. log
Function to show variables logging, with timestamps and caller info.

- It has built-in str.format - so such 2 calls are identical:
    log(s, args, kwargs)
    log(s.format(args, kwargs))
- Automatic duration time calculation
- Automatic detection of caller info

Examples:
Simple call
    log('a={}', 1)
    Prints to sys.stdout this string:
    [12.34"]fn:123 a=1
    Where:
    [12.34"]        Total elapsed time, from the moment of logging start.
    fn              Name of module/function/method caller.
    123             Index of line, where log is called.

Other features
    log('###')      Prints additional line with call stack.
                    ### fn:123 fn2:354 <module>:89
    log('¬¶')       Automatic replacement of "¬" to chr(9), "¶" to chr(10).

Redirection of output
    To output logging to file dir/my.log, do this:
        Tr.tr=Tr('dir/my.log')
    To return logging back to sys.stdout, do this:
        Tr.tr=Tr()

============
2. (i18n) get_translation
Utility to substitute strings via current CudaText translation.
How to use:
    In your module do assignment
        _   = get_translation(__file__)
    In places, where you want to translate strings, do this
        msg(_('my text'))

After that, collection of all such constants, and their translation, are possible via
- Standard Python utility pygettext
- Application like Poedit
Switching of translations is performed in sync with CudaText.

============
3. Saving/loading of data to/from JSON format.
Purpose is to give plugins the utility to store their settings.
Saving
    def set_hist(key_or_path,
                 value=None,
                 module_name='_auto_detect',
                 kill=False,
                 to_file=PLING_HISTORY_JSON)
Loading
    def get_hist(key_or_path,
                 default=None,
                 module_name='_auto_detect',
                 to_file=PLING_HISTORY_JSON)

- Location of file.
File name is given by parameter to_file.
If it's missed, then used "settings/plugin history.json".
If value of to_file is not the full path, then the path of "settings" folder is used.

- Sharing of settings.
For different plugins to be able to store their settings in a single file,
use parameter "module_name". If it's not set, then JSON file will have a branch with the
module name, from which set_hist/get_hist were called. Or you can set this branch by parameter.
If module_name=None, then branch will not be created, and all data will go to JSON root.
This may be handy, when plugin uses its own file.

- Location in file.
Parameter key_or_path specifies the key in JSON file, which will be stored/loaded.
It can be string - then it's location of the key (it can be inside module_name branch).
It can be list of string - then it's list of nested nodes of JSON tree.
On saving, all nodes are created automatically.
    But if existing JSON node is specified as intermediate node, library gives KeyError.

- Deletion of keys/branches.
If in set_hist you set kill=True, and key/branch specified by "key_or_path", exists,
then it will be deleted. In this case, parameter "value" is ignored.

- Comments and custom formatting (indents and spaces) are not kept on saving.
They are kept only in user.json, on saving via set_opt.

- Return.
In loading, if any of intermediate keys missed, or the final key is missed, you'll get default.
In saving, you'll get:
- parameter "value" value, if it's successfully saved.
- value previously stored by "key_or_path", if you used kill=True, and deletion performed.
- None, if you used kill=True, but key was not found.

============
4. Misc
- Short names
odict       = collections.OrderedDict
T,F,N       = True, False, None
c13,c10,c9  = chr(13),chr(10),chr(9)

- Short call of str.format
Instead of
    msg('a {}, b {}'.format('A', 'B'))
you can use
    msg(f('a {}, b {}', 'A', 'B'))

- Command to run current Python file, like it's CudaText plugin:
    "Execute current file as plugin"
Saves current file.
Clears console output.
Runs the file.
