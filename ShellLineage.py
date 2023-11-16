#The purpose of this script is to generate lineage of nested shell scripts and copy the files with their path to a given location#
#This script recurses through the shell script provided and drills down to the lowest level of shell scripts while trying to \n#
#resolve variables that are encountered in the parent as well as child scripts.#
#Args - "application|jobname|parentshellscript|arg1|arg2.." "envfile1|envfile2.."
#If env files are provided this script will try to resolve the variables in the env files first and try to resolve them in calls in subsequent shell scripts.#

import os
import sys
import re
import shutil
from collections import defaultdict

args = sys.argv
file = args[1].split('|')[2]
#print(file)
jobname = args[1].split('|')[1]
param = args[1].split('|')[3:]
appname = args[1].split('|')[0]
envfile = args[2]# if args[2] else ''
basedir = '/'.join(file.split('/')[:-2])
scriptdir = '/'.join(file.split('/')[:-1])
vars = None
filewrite = jobname+'.txt'
filemissing1 = jobname+'_failtocopy.txt'
try:
    os.remove(filewrite)
    os.remove(filemissing1)
except Exception as e:
    print("unable to delete "+filewrite+" "+filemissing1)

def getvars(file):
    dic = {}
    filesource = file
    with open(filesource,'r') as f:
        var = f.readlines()

    for line in var:
        if (line.strip().startswith('EXPORT') or line.strip().startswith('export')) and '=' in line.strip():
            line = line.strip('export').strip('EXPORT').strip()
            dic[line.split('=')[0]] = line.split('=')[1]
        elif re.match('[\w]+\=.+',line.strip()) and not line.strip().startswith('#'):
            #print('here',line)
            dic[line.strip().split('=')[0]] = line.strip().split('=')[1]

    return dic

appenv = {}
if envfile:
    for i in envfile.split('|'):
        appenv.update(getvars(i))
    for i in appenv:
        if 'script' in i.lower() and 'dir' in i.lower():
            appenv[i] = scriptdir
        elif 'base' in i.lower() and 'dir' in i.lower():
            appenv[i] = basedir

for p,q in enumerate(param):
    exec("appenv['{0}'] = '{1}'".format(p+1,q))
dict = defaultdict(list)
def recfile(file, dic = None):
    #print('running '+file)
    basedir = '/'.join(file.split('/')[:-2])
    scriptdir = '/'.join(file.split('/')[:-1])
    with open(file,'r') as fr:
        filecon = fr.readlines()
    fc = '\n'.join([i.strip() for i in filecon if not i.strip().startswith("#")])
    
    #Check for project.env
    if 'script' in file.split('/')[-2].lower():
        pth = '/'.join(file.split('/')[:-1])
        filesinpth = os.listdir(pth)
        envfile = '/'.join(file.split('/')[:-1])+'/project.env'
        if os.path.isfile(envfile):
            #print("envfile found")
            appenv.update(getvars(envfile))
        elif any('.env' in i for i in filesinpth):
            for efile in filesinpth:
                if efile.endswith('.env'):
                    #print(pth+'/'+efile)
                    appenv.update(getvars(pth+'/'+efile))

            #pass#print("env not found")

    vars = getvars(file)
    appenv.update(vars)
    vars = appenv
    for i in vars:
        if ('script' in i.lower() or 'scrpt' in i.lower()) and 'dir' in i.lower():
            vars[i] = scriptdir
        elif 'base' in i.lower() and 'dir' in i.lower():
            vars[i] = basedir
   
    for i in vars:
        if '$' in vars[i]:
            rep1 = re.findall('\$\{\w+\}',vars[i])
            rep2 = re.findall('\$\w+',vars[i])
            for j in rep1:
                try:
                    vars[i] = vars[i].replace(j,vars[j.strip('$').strip('{').strip('}')])
                except Exception as e:
                    pass#rint('warn:'+j+' not found')
            for k in rep2:
                    #print('$'+k)
                try:
                    vars[i] = vars[i].replace(k,vars[k.strip('$')])
                except Exception as e:
                    pass#print('warn:'+k+' not found')
    #if 'VSPJob' in vars:
        #print(vars['VSPJob'],'here',file)
    for key in vars.keys():
            #print(line,key)
            try:
                fc = fc.replace('$'+key, vars[key]).replace('${'+key+'}',vars[key])
                #print(line)
            except Exception as e:
                pass#print('warn'+key+' not found')
    sub_files_py = re.findall("[\w\/\$\{\}\.\-\=\'\"]{2,}\.py",fc)
    sub_files_sh = re.findall("[\w\/\$\{\}\.\-\=\'\"]{2,}\.sh[ \w\/\$\{\}\.]*",fc)
    sub_files_hql = re.findall("[\w\/\$\{\}\.\-\=\'\"]{2,}\.hql",fc)
    sub_files_dxj = re.findall("[\w\/\$\{\}\.\-\=\'\"]{2,}\.dxj",fc)
    sub_files_dxt = re.findall("[\w\/\$\{\}\.\-\=\'\"]{2,}\.dxt",fc)
    sub_files_py.extend(sub_files_sh)
    sub_files_py.extend(sub_files_hql)
    sub_files_py.extend(sub_files_dxj)
    sub_files_py.extend(sub_files_dxt)
    sub_files = sub_files_py
    ac_files = list(sub_files)
    ac_files_rep = []
    for line in ac_files:
        if len(vars)>0 and '$' in line:
            for key in vars.keys():
                try:
                    line = line.replace('$'+key, vars[key]).replace('${'+key+'}',vars[key])
                except Exception as e:
                    print('warn'+key+' not found')
            line = line.strip().replace('\'','').replace('\"','')
            line = line.replace('/somefolder/','/somefolder2.1/').replace('/somefolder2/','/somefolder21.0/')#.replace(' ','')
            #ac_files_rep.append(line)
        else:
            line = line.strip().replace('\'','').replace('\"','')
            line = line.replace('/somefolder/','/somefolder2.1/').replace('/somefolder2/','/somefolder21.0/')
        if '=' in line:
            line = line.split('=')[1]
        ac_files_rep.append(line)
    files_to_write = list([i.split(' ')[0] for i in ac_files_rep])
    files_to_write.append(file.split(' ')[0])
    files_to_write = list(set(files_to_write))
    with open(filewrite,'a') as fw:
        for i in files_to_write:
            fw.write(i+'\n')
    filemissing = []
    for i in files_to_write:
        if os.path.isfile(i.strip()):
            src = i.strip()
            dst = "/root/folder1/folder2/"+appname+src
            dstfolder = os.path.dirname(dst)
            if not os.path.exists(dstfolder):
                os.makedirs(dstfolder)
            shutil.copy(src,dst)
        else:
            filemissing.append(i.strip())
    if filemissing:
        with open(filemissing1,'a') as fw:
            for i in filemissing:
                fw.write(i+'\n')
    dict[file].append(list(set(ac_files_rep)))
    if ac_files_rep:
        #print(ac_files_rep)
        #if any('.sh' in file for file in ac_files_rep):
        ac_files_rep2 = [i for i in ac_files_rep if '.sh' in i]
        #print(ac_files_rep2)
        for sfile in ac_files_rep2:
                #print("running " +sfile)
            #if '.sh' in sfile:
            #print('true',sfile)
            param = sfile.split(" ")[1:]
            fname = sfile.split(" ")[0]
            #vars['0'] = fname
            for p,q in enumerate(param):
                exec("vars['{0}'] = '{1}'".format(p+1,q))
            try:
                recfile(fname.replace(' ','').strip(), dict)
            except Exception as e:
                if '/' in e:
                    print("unable to open ",fname.replace(' ','').strip(),e)
            #else:
                #continue
        #else:
            #print('no sh '+file)
            #return dict
    return dict
    
def writelineage(dc):
    with open(jobname+"_lineage.txt",'w') as lw:
        lw.write(str(a))

if __name__ ==  "__main__":
    #print('start')
    a = recfile(file)
    writelineage(a)
    #print('end')
