import os
import gzip
from shutil import copy
count = 0
def unzip(path):
    for root,dirs,files in os.walk(path):

        #解压

        for f in files:
            print(os.path.join(root,f))
            filename = os.path.join(root,f)
            if filename.find('.gz') >= 0:
                f_name = filename.replace('.gz','')
                g_file = gzip.GzipFile(filename)
                open(f_name,'wb+').write(g_file.read())
                g_file.close()

#复制 and 执行

def exe(file):
    for root,dirs,files in os.walk(file):

        rootdir = os.getcwd()
        for d in dirs:
            target = os.path.join(root,d)
            print(os.path.join(root,d))
            copy('./decoder',target+'/'+'decoder')
            os.chdir(target)
            os.system('./decoder > trace.txt')
            os.chdir(rootdir)


# 整理
def rmpsb(filename,savename):
    with open(filename,'r') as f:
        count = 0
        lens = 0
        # lens = len(f.readlines())
        flag = 0
        with open(savename,'w') as write:
            for line in f.readlines():
                # print(line)
                if line.find("AIR") >= 0:
                    print(f,line)
                    exit()
                if (line.find('tip')>=0 or line.find('tnt')>=0) and line.find('=') < 0:
                    lens += 1
                    
                    if flag == 1 and line.find("pge") >= 0:                       
                        continue
                    flag = 0
                    if(int(line.split(' ')[1],16)==0 and line.find("pgd") >= 0):
                        flag = 1
                        continue 
                    write.write(line)
        # if count > 0.01 * lens: 
        #     print("ERROR"+filename+' '+savename)
        #     os.system('rm -f '+savename)
                    # if line.find('tip.pge')>=0: line = 'tip.pge\n'
                    
def clean(soudir,tardir):
    global count
    # os.mkdir(tardir)
    for root,dirs,files in os.walk(soudir):
        for f in files:
            filename = os.path.join(root,f)
            print(filename,count)
            # print(filename.split(os.path.sep))
            if filename.find('trace.txt') >= 0:   
                # print(filename)
                rmpsb(filename,tardir+'/trace_no'+str(count)+'.txt')
            if filename.find('mapping.txt') >= 0 and filename.find('.gz') < 0:
                copy(filename,tardir+'/mapping_no'+str(count)+'.txt')
                count += 1

                 
def main():
    path_benign='./benign/'
    path_malicious = './malicious/'
    # unzip(path_malicious)
    # exe(path_malicious)
    # unzip(path_benign)
    # exe(path_benign)
    clean(path_benign,'./data/benign_data/')
    clean(path_malicious,'./data/malicious_data/')

if __name__ == '__main__':
    main() 