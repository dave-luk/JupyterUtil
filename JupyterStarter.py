from appJar import gui
from tkinter.filedialog import askdirectory
from subprocess import *
import os, psutil
import io
import signal
import platform
import sys
import webbrowser

script = 'jupyter notebook --no-browser > temp_{}.log 2>&1'

serverList = []
pathList = []
addrList = []
def start(button):
	if not app.getEntry('path') == '':
		path = str(app.getEntry('path'))
		pathList.append(path)
		serverList.append(None)
		addrList.append(None)
		name = path.split('/')
		name = name[len(name)-1]
		app.addListItem('serverList', name)
		name = name.replace(' ', '_')
		app.threadCallback(jupyter_starter, nb_callback, path, name, len(pathList)-1)
		
def stop(button):
	result = app.getListBox('serverList')
	if result:
		dir_selected = result[0]	
		index_selected = app.getAllListItems('serverList').index(dir_selected)
		process = serverList[index_selected]
		path = pathList[index_selected]
		
		if not process == None:
			if process.poll() == None:
				kill_proc_tree(process.pid, False)
				print('[instance terminated]', dir_selected, index_selected, process)
				#clean up
				app.removeListItemAtPos('serverList', index_selected)
				serverList.pop(index_selected)
				pathList.pop(index_selected)
				name = dir_selected.replace(" ",'_')
				os.remove('{}/temp_{}.log'.format(path,name))
		else:
			print('no process selected')
		
def launch(button):
	result = app.getListBox('serverList')
	if result:
		try:
			dir_selected = result[0]	
			index_selected = app.getAllListItems('serverList').index(dir_selected)
			addr = addrList[index_selected]
			webbrowser.open(addr, new=2 , autoraise=True)
		except:
			pass
		
def sel_dir(button):
	dir_name = askdirectory()
	app.setEntry('path', dir_name)

def jupyter_starter(path, name, index):
	kwargs = {}
	#if platform.system() == 'Windows':
	#	# from msdn [1]
	#	CREATE_NEW_PROCESS_GROUP = 0x00000200  # note: could get it from subprocess
	#	DETACHED_PROCESS = 0x00000008          # 0x8 | 0x200 == 0x208
	#	kwargs.update(creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP)  
	#elif sys.version_info < (3, 2):  # assume posix
	#	kwargs.update(preexec_fn=os.setsid)
	#else:  # Python 3.2+ and Unix
	#	kwargs.update(start_new_session=True)
	#
	
	sub = Popen(script.format(name), stdin=None, stdout=None, cwd=path, bufsize=1, universal_newlines=True, shell=True, **kwargs)	
	
	return sub, path, name, index

def kill_proc_tree(pid, including_parent=True):    
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    for child in children:
        child.kill()
    gone, still_alive = psutil.wait_procs(children, timeout=5)
    if including_parent:
        parent.kill()
        parent.wait(5)
	
def nb_callback(args):
	sub, path, name, index = args
	serverList[index] = sub
	app.threadCallback(infoReader, updateInfo, path, name, index)
	
def infoReader(path, name, index):
	finished = False
	while not finished:
		tf = open(path+'/temp_{}.log'.format(name), 'r')
		for line in tf.readlines():
			if "http://" in line:
				addr = line.split(' ')[3].replace('\n','')
				print(addr)
				return addr, index
	
def updateInfo(args):
	addr, index = args
	addrList[index] = addr
	
# general settings
app = gui("Jupyter Starter")
app.setResizable(False)
app.setBg('darkgreen')
app.setButtonFont(12)
app.setLabelFont(18)

# banner
app.addLabel("title", "Start Jupyter on directory", 0, 0, 9)
app.setLabelBg("title", "gold")

app.addEntry('path', 1,0,7,1).bind('<1>',sel_dir)
app.setEntryDefault('path', 'enter path')
app.addButton('Directory', sel_dir, 1,7,2,1)

app.addListBox('serverList',serverList, 2,0,9,8)
app.setListBoxMulti('serverList', False)


app.addButton('Stop', stop, 10,0,3,1)
app.setButtonBg('Stop', 'red')
app.addButton('Launch', launch, 10,3,3,1)
app.setButtonBg('Launch', 'yellow')
app.addButton('Start', start, 10,6,3,1)
app.setButtonBg('Start','green')
#specs
app.setButtonWidth('Directory', 20)
app.setButtonWidth('Start', 33)
app.setButtonWidth('Launch', 33)
app.setButtonWidth('Stop', 33)
app.setEntryWidth('path', 50)

app.go()

