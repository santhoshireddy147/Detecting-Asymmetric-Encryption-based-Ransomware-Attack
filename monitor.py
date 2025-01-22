import os
import time
import psutil
import subprocess
import sys
import re
import threading
from tkinter import *
import tkinter as tk
from tkinter import messagebox
from subprocess import call
#from auditd_tools.event_parser import AuditdEventParser
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime, timedelta

class FileModifiedHandler(FileSystemEventHandler):
    def __init__(self):
        super(FileModifiedHandler, self).__init__()
        self.recently_modified_files = []
   
   

    def on_modified(self, event):
        #print(event)
        if event.is_directory:
            return

        file_path = event.src_path
        file_name = os.path.basename(file_path)
        result = file_path.rsplit('/', 1)[0]
        #print(result)
        self.recently_modified_files.append(result)

        
        #pid = get_file_pid(file_path)
        
        #process_info = get_modifying_process_info(event.src_path)
        print(f'File {event.src_path} has been modified')
        before = timestamp = datetime.fromtimestamp(os.stat(file_path).st_mtime)
        now = datetime.now()
        
        #print(timestamp)
        auparam = " -sc EXECVE"
        #cmd = "sudo ausearch -ts " + before.strftime('%H:%M:%S') + " -te " + now.strftime('%H:%M:%S')   + auparam
        cmd = "sudo ausearch --start now --end now -k target_dir"
        #cmd = "sudo ausearch -k target_dir"
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        res = p.stdout.read().decode()
        #print(res)
        
        pid_pattern = re.compile(r' pid=(\d+)')
        pname_pattern = re.compile(r' comm="([^"]+)"')

        
        match = pid_pattern.search(res)
        match2 = pname_pattern.search(res)
        if match or match2:
            
            root = tk.Tk()
            #root.withdraw()
            pid = match.group(1)
            pname=match2.group(1)
            print(f"Pname: {pname}")
            
            cmd ="sudo kill -STOP "+pid
            call(cmd, shell=True)
            print('PID '+pid+ ' with name '+pname+' paused')
            
            root.eval('tk::PlaceWindow %s center' % root.winfo_toplevel())
            root.withdraw()
            msg = 'pid ' +pid +' is modifing files.  Kill the process? click YES to kill process'
            if messagebox.askyesno('Alert',msg,icon ='error')==True:
                  cmd ="sudo SIGKILL"+pid
                  call(cmd, shell=True)
                  print('PID '+pid+' with name '+pname+' killed')
                  
                  root.deiconify()
                  root.destroy()
                  root.quit()
            else:
                 cmd ="sudo kill -CONT "+pid
                 call(cmd, shell=True)
                 print('PID '+pid+' with name '+pname+' resumed')
                 
                 root.deiconify()
                 root.destroy()
                 root.quit()
            root.mainloop()
            #USER_INP = popupWindow.askstring(self.root, title="Test",prompt="What's your Name?:")
            #user_input = self.show_popup(pid)
            #user_input = inotify_user(pid)
            #time.sleep(30)
        
            #cmd ="sudo kill -CONT "+pid
            #call(cmd, shell=True)
            #print('continued')
            
        else:
            print('not pid found')
            
            
def watchdog(directory_path, time_interval=10):
    
    
    event_handler = FileModifiedHandler()
    observer = Observer()
    observer.schedule(event_handler, directory_path, recursive=False)
    observer.start()
    #root.after(1000, root.mainloop)
    

    try:
        while True:
         time.sleep(1)
         #root.mainloop()
            #pass
    except KeyboardInterrupt:
        observer.stop()
        

    observer.join()
    

if __name__ == "__main__":
    directory_to_monitor = "/home/hk0648/ransomware/target"
    watchdog(directory_to_monitor)
    
    


