# Stupid GDB Helper for PHP
# Author: Juan Manuel Fernandez (@TheXC3LL)
# Website: x-c3ll.github.io


import gdb
import subprocess
import sys

print("\033[1m\033[41m[+] Stupid GDB Helper for PHP loaded! (by @TheXC3LL)\033[0m")



class zifArgsError(gdb.Command):
    "Tries to infer parameters from PHP errors"

    def __init__(self):
        super(zifArgsError, self).__init__("zifargs_error", gdb.COMMAND_SUPPORT, gdb.COMPLETE_NONE,True)

    def invoke(self, arg, from_tty):
        payload = "<?php " + arg + "();?>"
        file = open("/tmp/.zifargs", "w")
        file.write(payload)
        file.close()
        try:
            output = str(subprocess.check_output("php /tmp/.zifargs 2>&1", shell=True))
        except:
            print("\033[31m\033[1mFunction " + arg + " not defined!\033[0m")
            return
        try:
            number = output[output.index("at least ")+9:output.index("at least ")+10]
        except:
            number = output[output.index("exactly ")+8:output.index("exactly")+9]
        #print("\033[33m\033[1m" + arg+ "(\033[31m" + number + "\033[33m): \033[0m")
        params = []
        infered = []
        i = 0
        while True:
            payload = "<?php " + arg + "("
            for x in range(0,int(number)-len(params)):
                params.append("'aaa'")
            payload += ','.join(params) + "); ?>"
            file = open("/tmp/.zifargs", "w")
            file.write(payload)
            file.close()
            output = str(subprocess.check_output("php /tmp/.zifargs 2>&1", shell=True))
            #print(output)
            if "," in output:
                separator = ","
            elif " file " in output:
                params[i] = "/etc/passwd"
                infered.append("\033[31mPATH")
                i +=1
            elif " in " in output:
                separator = " in "

            try:
                dataType = output[:output.rindex(separator)]
                dataType = dataType[dataType.rindex(" ")+1:].lower()
                if dataType == "array":
                    params[i] = "array('a')"
                    infered.append("\033[31mARRAY")
                if dataType == "callback":
                    params[i] = "'var_dump'"
                    infered.append("\033[33mCALLABLE")
                if dataType == "int":
                    params[i] = "1337"
                    infered.append("\033[36mINTEGER")
                i += 1
                #print(params)
            except:
                if len(infered) > 0:
                    print("\033[1m" + ' '.join(infered) + "\033[0m")
                    return
                else:
                    print("\033[31m\033[1mCould not retrieve parameters from " + arg + "\033[0m")
                    return



class zifArgs(gdb.Command):
    "Show PHP parameters used by a function. Symbols needed."

    def __init__(self):
        super (zifArgs, self).__init__("zifargs", gdb.COMMAND_SUPPORT, gdb.COMPLETE_NONE, True)

    def invoke (self, arg, from_tty):
        size = 10
        while True:
            try:
                sourceLines = gdb.execute("list zif_" + arg, to_string=True)
            except:
                try:
                    sourceLines = gdb.execute("list php_" + arg, to_string=True)
                except:
                    try:
                        sourceLines = gdb.execute("list php_if_" + arg, to_string=True)
                    except:
                        print("\033[31m\033[1mFunction " + arg + " not defined!\033[0m")
                        return
            if "ZEND_PARSE_PARAMETERS_END" not in sourceLines:
                size += 10
                gdb.execute("set listsize " + str(size))
            elif "zend_parse_parameters_none" in sourceLines:
                gdb.execute("set listsize 10")
                print("\033[90mVOID\033[0m")
                return
            else:
                gdb.execute("set listsize 10")
                break
        try:
            chunk = sourceLines[sourceLines.index("_START"):sourceLines.rindex("_END")].split("\n")
            #print(chunk)
        except:
            print("\033[31m\033[1mParameters not found. Try zifargs_old <function>\033[0m")
            return
        params = []
        for x in chunk:
            if "Z_PARAM_ARRAY" in x:
                params.append("\033[31mARRAY")
            if "Z_PARAM_ARRAY_OR_OBJECT" in x:
                params.append("\033[31mARRAY_OR_OBJECT")
            if "Z_PARAM_ARRAY_HT" in x:
                params.append("\033[31mARRAY_HT")
            if "Z_PARAM_ARRAY_OR_OBJECT_HT" in x:
                params.append("\033[31mARRAY_OR_OBJECT_HT")
            if "Z_PARAM_BOOL" in x:
                params.append("\033[32mBOOL")
            if "Z_PARAM_FUNC" in x:
                params.append("\033[33mCALLABLE")
            if "Z_PARAM_DOUBLE" in x:
                params.append("\033[34mDOUBLE")
            if "Z_PARAM_LONG" in x or "Z_PARAM_STRICT_LONG" in x:
                params.append("\033[36mLONG")
            if "Z_PARAM_ZVAL" in x:
                params.append("\033[37mMIXED")
            if "Z_PARAM_OBJECT" in x:
                params.append("\033[38mOBJECT")
            if "Z_PARAM_RESOURCE" in x:
                params.append("\033[39mRESOURCE")
            if "Z_PARAM_STR" in x:
                params.append("\033[35mSTRING")
            if "Z_PARAM_PATH_STR" in x:
                params.append("\033[31mPATH")
            if "Z_PARAM_CLASS" in x:
                params.append("\033[37mCLASS")
            if "Z_PARAM_PATH" in x:
                params.append("\033[31mPATH")
            if "Z_PARAM_OPTIONAL" in x:
                params.append("\033[37mOPTIONAL")
            if "Z_PARAM_VARIADIC" in x:
                params.append("\033[90mVARIADIC")
        if len(params) == 0:
            print("\033[31m\033[1mParameters not found. Try zifargs_old <function> or zifargs_error <function>\033[0m")
            return
        print("\033[1m"+' '.join(params) + "\033[0m")




zifArgs()
zifArgsError()
