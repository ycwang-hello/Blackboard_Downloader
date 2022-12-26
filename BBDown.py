# -*- coding: utf-8 -*-
"""
Created on Fri Jan  1 12:40:33 2021

@author: Yu-Chen Wang
"""

import selenium
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import re
import os
import shutil
import numpy as np
import pickle

class NotFoundError(Exception):  
    def __init__(self, err):
        Exception.__init__(self,err)
class UnexpectedError(Exception):  
    def __init__(self, err):
        Exception.__init__(self,err)
        
class FailedToDoError(Exception):  
    def __init__(self, task, real_exception=None):
        err = 'Failed to ' + task.info        
        Exception.__init__(self, err)
        self.real_exception = real_exception
        
def task_info(info):
    def wrapper(f):
        f.info = info
        return f
    return wrapper
        
def try_to(task, maxtry=100, interval=1):
    for i in range(maxtry):
        try:
            task()
        except:
            if i == maxtry-1:
                raise FailedToDoError(task)
            time.sleep(interval)
        else:
            break

def click(find_by, value):
    @task_info(f'click the object for "{find_by}" == "{value}"')
    def f():
        # f.info = f'click the object for {find_by} == {value}'
        driver.find_element(by=find_by, value=value).click()
    return f

def select_one(l, morestr=''):
    for i in range(len(l)):
        print('{}\t{}'.format(i, l[i]))
    idx = input('Choose one index {}: >>> '.format(morestr))
    if idx.isdigit():
        print('You have chosen "{}".'.format(l[int(idx)]))
        return int(idx)
    else:
        return idx

univ = input('Input your university (currently supported: "BNU" and "PKU") >>> ')
if univ == 'BNU':
    bb_url = 'https://bb.bnu.edu.cn/webapps/cas-bjsfdx-BBLEARN/index.jsp'
if univ == 'PKU':
    bb_url = 'https://course.pku.edu.cn/'
else:
    raise NotImplementedError(f'University "{univ}" is not supported.')

name_map_file = 'BBDown.names'
if os.path.exists(name_map_file):
    with open(name_map_file, 'rb') as f:
        name_mapping = pickle.load(f)
else:
    name_mapping = {}
# if not os.path.exists(name_map_file):
#     with open(name_map_file, 'w') as f:
#         f.write('BB_name,BB_path,')
tryext = ['txt', 'ppt', 'pptx', 'doc', 'docx', 'xls', 'xlsx', 'pdf', 'zip', 'rar', '7z', 'jpg', 'JPG', 'png']

def exclude(l):
    down = np.ones(len(l)).astype('bool')
    while True:
        for i in range(len(l)):
            print('{}\t{}\t{}'.format('' if down[i] else 'x', i, l[i]))
        print('Those with an x will not be downloaded.')
        print('example: \n0-7,9 for exclude\n^3 for include\ninput s to auto exclude existing files')
        idx = input('Input slices to exclude or include (o to finish): >>> ')
        if idx == 'o':
            return down
        if idx == 's':
            for i in range(len(l)):
                if os.path.exists(dirs[i]):
                    down[i] = False
                for ext in tryext:
                    if os.path.exists(dirs[i]+'.'+ext):
                        down[i] = False
                        break                
                if dirs[i] in name_mapping.keys():
                    if os.path.exists(name_mapping[dirs[i]]):
                        down[i] = False
                    for ext in tryext:
                        if os.path.exists(name_mapping[dirs[i]]+'.'+ext):
                            down[i] = False
                            break
            print('I have found some files that you may have already had. Check again.')
            time.sleep(1)
            continue
        try:
            if idx[0] == '^':
                idx = idx[1:].split(',')
                for i in idx:
                    if '-' in i:
                        a, b = i.split('-')
                    else:
                        a = i; b = i
                    down[int(a):(int(b)+1)]=True
            else:
                idx = idx.split(',')
                for i in idx:
                    if '-' in i:
                        a, b = i.split('-')
                    else:
                        a = i; b = i
                    down[int(a):(int(b)+1)]=False
        except:
            print('ERROR:check your input')
    
print('INFO: Files will be downloaded to current working directory: {}.'.format(os.getcwd()))
if not os.path.exists('temp'):
    os.mkdir('temp')
prefs = {
"download.default_directory": os.getcwd()+'\\temp',
"download.prompt_for_download": False,
"download.directory_upgrade": True,
"plugins.always_open_pdf_externally": True
}
options = webdriver.ChromeOptions()
options.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome(options=options)#ChromeDriverManager().install())#, chrome_options=option)

driver.get(bb_url)#('http://bb.bnu.edu.cn/webapps/cas-bjsfdx-BBLEARN/index.jsp')
print('Log in, and come back here')
while True:
    # try:
    #     driver.switch_to.frame('content')
    # except:
    #     pass
    src = driver.page_source
    soup = BeautifulSoup(src,features="html.parser")
    courses = soup.find('ul', {'class': re.compile('.courseListing.')})#.find_all('a')
    if courses == None:
        time.sleep(1)
    else:
        courses = courses.find_all('a')
        break
print('WARNING: from now on, do not use Chrome unless you are asked to do so.')

courses = [course.string for course in courses]
print('Choose one course:')
course = courses[select_one(courses)]

driver.find_element_by_link_text(course).click() 
for i in range(100):
    try:
        driver.switch_to.frame('content')
    except:
        print('Error switching to frame "content", will retry...')
        if i == 0:#2:
            print('failed switching to frame "content"')
            break
        time.sleep(1)
    else:
        break
driver.maximize_window()
# driver.find_element_by_id('menuPuller').click()
try_to(click('id', 'menuPuller'))
trytxt = ['教学内容', '课程文档', '文档', '内容', '课件资料下载']
success = False
root = None
for txt in trytxt:
    try:
        # driver.find_element_by_link_text(txt).click()
        try_to(click('link text', txt), 2, 2)
    # except Exception as error: #(selenium.common.exceptions.NoSuchElementException, AttributeError):
    #     if isinstance(error.real_exception, selenium.common.exceptions.NoSuchElementException) or isinstance(error.real_exception, AttributeError):
    #         print("INFO: {} not found".format(txt))
    #         continue
    #     else:
    #         raise
    except FailedToDoError:
        print(f'INFO: failed to click {txt}')
        continue
    except:
        raise
    else:
        print("INFO: entering {}".format(txt))
        root = txt
        success = True
        break
if not success:
    while True:
        txt = input('ERROR: I cannot find names in {}. Please input the name >>> '.format(trytxt))
        try:
            driver.find_element_by_link_text(txt).click()
        except selenium.common.exceptions.NoSuchElementException:
            print("INFO: {} not found, try again.".format(txt))
            continue
        except:
            raise
        else:
            print("INFO: entering {}".format(txt))
            root = txt
            break

print('Please check if Chrome has entered the page to download the files. If not, the program may fail, but you may manually enter it.')

#### FIND FILES
ind = ''#s'.   '
dirs = []
names = []
new_dirs = []
down_urls = []
down_url_sites = [] #url where I can find down url
path = ''

### define download methods
#1. down by tree
def search_in_tree(ul):
    global path, ind 
    lis = ul.findAll('li', recursive=False)
    for li in lis:
        ul = li.findAll('ul', recursive=False)
        if len(ul) == 0: # I find a file
            a = li.find('a', {'class': 'tocItem'}, recursice=False)
            name = a.string
            print(ind+name)
            dirs.append(path+name)
            names.append(name)
            url = 'http://bb.bnu.edu.cn'+a.get('onclick').split("'")[1]
            down_urls.append(url)
            down_url_sites.append(driver.current_url)
        elif len(ul) == 1: # I find a folder
            ul = ul[0]
            name = li.find('a', {'class': re.compile(".tocFolder")}, recursice=False).string
            print(ind+name+' [dir]')
            path += (name + '/')
            if not os.path.exists(path):
                new_dirs.append(path)
            ind += '.   '
            search_in_tree(ul)
        else:
            raise UnexpectedError('Err No. 2, len(ul) > 1?')
    ind = ind[:-4]
    path = '/'.join(path.split('/')[:-2])
    if path != '':
        path += '/'

def find_tree(les_name):
    try:
        driver.switch_to.frame('content')
    except:
        pass
    timeout = 10
    t0 = time.time()
    while True:
        time.sleep(1)
        src = driver.page_source
        page = BeautifulSoup(src,features="html.parser")
        treeuls = page.find_all('ul', id='tocTree')
        if len(treeuls) == 1:
            treeul = treeuls[0]
            search_in_tree(treeul)
            break
        elif len(treeuls) == 0:
            if time.time() - t0 > timeout:
                raise NotFoundError('tree not found')
        else:
            raise UnexpectedError('Error number 1. Please contact the author.')

def decide_method(classstr):
    if 'folder' in classstr: #find folder
        return find_in_folder 
    elif 'lesson' in classstr: #lesson uses tree
        return find_tree
    elif 'document' in classstr: #document, download!
        # return 'file' #add_file
        return 'document' #inferred dir
    elif 'file' in classstr: #document, download!
        return 'file' #add_file
    elif 'cal_year_event' in classstr: #document, download!
        return 'file' #add_file
    else:
        return 'ERROR: unrecognized class string "{}".'.format(classstr)

def find_in_folder(foldername): #find file in a folder
    global path, ind 
    for i in range(30):
        src = driver.page_source
        soup = BeautifulSoup(src,features="html.parser")
        courses = soup.find('ul', {'class', 'contentList'})
        if courses == None:
            time.sleep(1)
        else:
            flist = courses.find_all('li', recursive=False)
            break    
    for fi in flist:
        #########
        # if fi.get('class') == ['clearfix', 'read']:
        #     fs = fi.findAll('li')
        #     itemname = fi.find('div', class_="item clearfix").get_text(strip=True)
        #     print(ind+itemname+' [inferred dir]')
        #     path += (itemname + '/')
        #     ind += '.   '
        #     if not os.path.exists(path):
        #         new_dirs.append(path)
        # else:
        #     fs = [fi]
        # for f in fs:
        ##########
        f = fi
        if True:
        ##########

# TODO: a.find change to a.findAll, since there may be more than one link for an item.
# TODO: currently changed to a.findAll, but only the first is used.
            as_ = f.findAll('a')
            if len(as_) == 0:
                print(ind+'ERROR: something without a link')
                continue
            for a in as_:
                # if a == None:
                #     print(ind+'ERROR: something without a link')
                #     continue

                # check if it is really a file link
                if a.get('title') == '单击获得更多选项':
                    continue

                name = a.get_text(strip=True)
                if name is None: # try other ways to get file name
                    name = a.find('span')#.string
                    if name is not None:
                        name = name.string
                    if name is None: # name is still None?
                        name = a.string#.replace()
                if name in ['', None]:
                    print(ind+'WARNING: something with unknown name')
                    name = '$UNKNOWN'
                    # print(a)
                    # raise KeyboardInterrupt
                classname = f.find('img').get('src').split('/')[-1]
                find = decide_method(classname)
                if find == 'file':
                    print(ind+name)
                    dirs.append(path+name)
                    names.append(name)
                    url = 'http://bb.bnu.edu.cn'+a.get('href')
                    down_urls.append(url)
                    down_url_sites.append(driver.current_url)
                elif find == 'document':
                    fs = fi.findAll('li')
                    itemname = fi.find('div', class_="item clearfix").get_text(strip=True)
                    print(ind+itemname+' [inferred dir]')
                    path += (itemname + '/')
                    ind += '.   '
                    if not os.path.exists(path):
                        new_dirs.append(path)
                    for f in fs:
                        for a in f.findAll('a'):
                            if a.get('title') == '单击获得更多选项':
                                continue
                            name = a.get_text(strip=True)
                            if name is None: # try other ways to get file name
                                name = a.find('span')#.string
                                if name is not None:
                                    name = name.string
                                if name is None: # name is still None?
                                    name = a.string#.replace()
                            if name in ['', None]:
                                print(ind+'WARNING: something with unknown name')
                                name = '$UNKNOWN'
                            classname = f.find('img').get('src').split('/')[-1]
                            assert decide_method(classname) == 'file'
                            print(ind+name)
                            dirs.append(path+name)
                            names.append(name)
                            url = 'http://bb.bnu.edu.cn'+a.get('href')
                            down_urls.append(url)
                            down_url_sites.append(driver.current_url)
                    path = '/'.join(path.split('/')[:-2])
                    if path != '':
                        path += '/'
                    ind = ind[:-4]

                    break # links in this inferred dir already handled; not consider the rest <a> any more

                elif find in [find_in_folder, find_tree]:
                    #get in folder
                    driver.find_element_by_link_text(name).click() 
                    time.sleep(.5)
                    print(ind+name+' [dir]')
                    path += (name + '/')
                    ind += '.   '
                    if not os.path.exists(path):
                        new_dirs.append(path)
                    #now search in the folder!
                    find(name)
                    #exit folder
                    driver.find_element_by_link_text(foldername).click() 
                    time.sleep(.5)
                    path = '/'.join(path.split('/')[:-2])
                    if path != '':
                        path += '/'
                    ind = ind[:-4]
                elif type(find) == str and 'ERROR' in find:
                    print(find)
                    print('Some files may be skipped. contact the author.')
                else:
                    raise UnexpectedError()

        ###########
        # if fi.get('class') == ['clearfix', 'read']:
        #     path = '/'.join(path.split('/')[:-2])
        #     if path != '':
        #         path += '/'
        #     ind = ind[:-4]
        ###########

find_in_folder(root)

cont = input('''
Start downloading the above file and folders? 
y: yes
n: no(default)
e: choose which to download, skip existing files
>>> ''')
if cont == 'y':
    down = np.ones(len(dirs)).astype('bool')
if cont == 'e':
    down = exclude(dirs)   
    cont = input('Start downloading the above file and folders? y(es) or n(o), default no >>> ')
if cont != 'y':
    raise KeyboardInterrupt('You have stopped the program. Welcome back!')

#use the name of the downloaded file? (otherwise use the name found on the BB)
use_bb_name = input('''
Use the name found on the BB or use the name of the downloaded file?
b: name on BB
d: name of the downloaded file
>>> '''
)
if use_bb_name == 'b':
    use_bb_name = True
elif use_bb_name == 'd':
    use_bb_name = False
else:
    print('use name on BB.')
    use_bb_name = True

# TODO: BUG in below 1 line: if names the same
# dirdict = dict(zip(names, dirs))
def download(url, url_site, diri, name):
    old_filel = os.listdir('temp')
    driver.get(url_site)
    #name: name of file found on the website
    if name[-4:] in ['.pdf', '.PDF']:
        try_to(click('link text', name), 2, 2)
        # driver.get(url) #this is refused, so I no longer do it
        #### Below is not corrected
        print('WARNING: pdf auto download not implemented')
        if False:
            try:
                driver.switch_to.frame('content')
            except:
                pass
            soup = BeautifulSoup(driver.page_source)
            link = soup.find('div',{'class':'item clearfix'}).find('a').get('href')
            driver.get('http://bb.bnu.edu.cn'+link)
    else:
        try_to(click('link text', name), 2, 2)
        # driver.get(url)
    t0 = time.time()
    while True:
        time.sleep(0.5)
        filel = os.listdir('temp')
        new_file = [file for file in filel if file not in old_filel]
        if len(new_file) > 0 and '.crdownload' not in ''.join(filel) and '.tmp' not in ''.join(filel): #downloaded
            if name in filel:
                f = name #f: real file name in "temp"
            else:
                print('WARNING: cannot find {}! Which of these IN "TEMP" folder is file for this?'.format(name))
                for i in range(len(filel)):
                    print(i, filel[i])
                ind = input('input the index, or "r" to reload >>> ')
                if ind in ['r', '']:
                    continue
                f = filel[int(ind)]
                print('INFO: you have chosen {}'.format(f))
            ext = '.'+f.split('.')[-1]
            if use_bb_name:
                pf = diri #dirdict[name] #pf: dest path to file
                print(f'{name} -> {pf}')
            else:
                pf = '/'.join(diri.split('/')[:-1] + [f]) # + '/' + f  # dirdict[name]
                print(f'{name} -> {f} -> {pf}')
                name_mapping[diri] = pf
                # with open()
            if pf[-8:] == '$UNKNOWN':
                print('Since I do not know the file name, I will use the name of the downloaded file.')
                pf = pf[:-8]+f
            if not ext in pf:
                pf += ext
            if os.path.exists(pf):
                if cho == 'o':
                    print('WARNING: {} overwritten.'.format(pf))
                    shutil.move('temp/'+f, pf)
                elif cho == 's':
                    print('INFO: {} skipped.'.format(pf))
                    shutil.move('temp/'+f, 'temp/TRASH_'+f)
                elif cho == 'a':
                    rep = input('WARNING: {} exists!\nOverwrite? (otherwise, will skip) y/n >>> '.format(pf))
                    if rep == 'y':
                        shutil.move('temp/'+f, pf)
                        print('INFO: {} overwritten.'.format(pf))
                    else:
                        print('INFO: {} skipped.'.format(pf))
                        shutil.move('temp/'+f, 'temp/TRASH_'+f)
            else:
                shutil.move('temp/'+f, pf)
                print('INFO: {} downloaded.'.format(pf))
                
            break
        # elif len(new_file) == 0 and time.time() - t0 > 3:
        #     driver.get(url)
        elif len(new_file) == 0 and time.time() - t0 > 3:
            print('You are downloading {}.'.format(name))
            ispdf = input('WARNING: Please check, it seems that download has not started. Type "y" if it is PDF, type "skip" to skip this, otherwise download it to "temp" dir by yourself. y/[n] >>> ')
            if ispdf == 'y':
                try:
                    driver.switch_to.frame('content')
                except:
                    pass
                try:
                    soup = BeautifulSoup(driver.page_source)
                    link = soup.find('div',{'class':'item clearfix'}).find('a').get('href')
                    driver.get('http://bb.bnu.edu.cn'+link)
                except (Exception, BaseException) as err:
                    print(err)
                    print('I don\'t think it is pdf.')
                time.sleep(0.5)
            elif ispdf == 'skip':
                print('You have skipped "{}".'.format(name))
                return

cho = input('''
INFO: Choose mode:
o: always overwrite existing files
s: skip existing files
a: ask whether to overwrite
>>> ''')
if cho not in ['o', 's', 'a']:
    cho = 'a'

for new_dir in new_dirs:
    os.mkdir(new_dir)
try:
    for name, diri, url, url_site, d in zip(names, dirs, down_urls, down_url_sites, down):
        if d:
            download(url, url_site, diri, name)
                # pickle.dump(name_mapping, name_map_file)
except:
    raise 
finally:
    with open(name_map_file, 'wb') as f:
        pickle.dump(name_mapping, f)

print('Congratulations, download completed without fatal errors!\nYou may close the Chrome and delete the files in temp directory.')

input('Press Enter to close Chrome...')
driver.close()
