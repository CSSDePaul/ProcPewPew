from Tkinter import *
import os
import threading

processes = []
services = []
scene = []
sceneCheck = 0

window = Tk()
window.title("ProcPewPew")

isActive = IntVar()
modeCheck = Checkbutton(window, text="Active",variable=isActive)
modeCheck.grid(row=0,column=0,sticky="w")

################################
processFrame = Frame(window,bd=5)
processFrame.grid(row=1,column=0)

processList = Listbox(processFrame,width=40,height=10)
processList.pack(side="left",fill="y")

processScroll = Scrollbar(processFrame,orient="vertical")
processScroll.config(command=processList.yview)
processScroll.pack(side="right",fill="y")
processList.config(yscrollcommand=processScroll.set)
################################
serviceFrame = Frame(window,bd=5)
serviceFrame.grid(row=2,column=0)

serviceList = Listbox(serviceFrame,width=40,height=10)
serviceList.pack(side="left",fill="y")

serviceScroll = Scrollbar(serviceFrame,orient="vertical")
serviceScroll.config(command=serviceList.yview)
serviceScroll.pack(side="right",fill="y")
serviceList.config(yscrollcommand=serviceScroll.set)
#################################
blacklistFrame = Frame(window,bd=10)
blacklistFrame.grid(row=1,column=1,rowspan=2,columnspan=2)

blacklistList = Listbox(blacklistFrame,width=40,height=20)
blacklistList.pack(side="left",fill="y")

blacklistScroll = Scrollbar(blacklistFrame,orient="vertical")
blacklistScroll.config(command=blacklistList.yview)
blacklistScroll.pack(side="right",fill="y")
blacklistList.config(yscrollcommand=blacklistScroll.set)
#################################
sceneFrame = Frame(window,bd=20)
sceneFrame.grid(row=3,column=0,columnspan=3)

sceneList = Listbox(sceneFrame,width=80,height=10)
sceneList.pack(side="left",fill="y")

sceneScroll = Scrollbar(sceneFrame,orient="vertical")
sceneScroll.config(command=sceneList.yview)
sceneScroll.pack(side="right",fill="y")
sceneList.config(yscrollcommand=sceneScroll.set)
#################################

def setup():
    tempBL = []
    with open("bl.txt","a+") as blFile:
        for item in blFile.read().split("\n"):
            if item != "" and item not in blacklistList.get(0,END):
                blacklistList.insert(0,item)
                tempBL.append(item)
    open("bl.txt","w").close()
    with open("bl.txt","a+") as blFile:
        for item in tempBL:
            blFile.write(item+"\n")

def add(item):
    if item != "" and item not in blacklistList.get(0,END):
        blacklistList.insert(0,item)
        open("bl.txt","w").close()
        with open("bl.txt","a+") as blFile:
            for ps in blacklistList.get(0,END)[::-1]:
                blFile.write(ps+"\n")
    addEntry.delete(0,END)

def delete(item):
    blacklistList.delete(blacklistList.get(0,END).index(item))
    open("bl.txt","w").close()
    with open("bl.txt","a+") as blFile:
        for ps in blacklistList.get(0,END)[::-1]:
            blFile.write(ps+"\n")
    
#################################
addEntry = Entry(window)
addEntry.grid(row=0,column=1,sticky="e")

addButton = Button(window,text="ADD",command=lambda:add(addEntry.get()))
addButton.grid(row=0,column=2,sticky="w",padx=5,pady=5)
#################################
processList.bind("<Return>",lambda event:add(processList.get(processList.curselection())))
serviceList.bind("<Return>",lambda event:add(serviceList.get(serviceList.curselection())))
sceneList.bind("<Return>",lambda event:add(sceneList.get(sceneList.curselection())))
blacklistList.bind("<Delete>",lambda event:delete(blacklistList.get(blacklistList.curselection())))
#################################

def updateScene(item):
    if item not in sceneList.get(0,END):
        sceneList.insert(0,item)

def updateProcess():
    global sceneCheck
    currentList = processList.get(0,END)
    for process in currentList:
        if process not in processes:
            processList.delete(currentList.index(process))
            try:
                scene.pop(scene.index(process))
            except:
                continue
    for process in processes:
        if process not in currentList:
            processList.insert(0,process)
        if process not in scene:
            scene.append(process)
            if sceneCheck:
                updateScene(process)

def updateService():
    global sceneCheck
    currentList = serviceList.get(0,END)
    for service in currentList:
        if service not in services:
            serviceList.delete(currentList.index(service))
            try:
                scene.pop(scene.index(service))
            except:
                continue
    for service in services:
        if service not in currentList:
            serviceList.insert(0,service)
        if service not in scene:
            scene.append(service)
            if sceneCheck:
                updateScene(service)

def remove(item):
    os.popen("taskkill /F /IM "+item)

def organize():
    global processes
    global services
    global sceneCheck
    temp = os.popen("tasklist").read().split("\n")
    clean = []
    for i in temp[3:len(temp)-1]:
        i = i.split()[:3]
        item = i[0]
        if ".exe" in item and "tasklist.exe" != item and "taskkill.exe" != item:
            clean.append(i)
    tempProcesses = []
    tempServices = []
    for i in clean:
        item = i[0]
        if item in blacklistList.get(0,END):
            remove(item)
            updateScene(item)
        elif isActive.get() and item in sceneList.get(0,END):
            remove(item)
            updateScene(item)
        else:
            if i[2] == "Console" and item not in tempProcesses:
                tempProcesses.append(item)
            elif i[2] == "Services" and item not in tempServices:
                tempServices.append(item)
    if tempProcesses != processes:
        processes = tempProcesses
        updateProcess()
    if tempServices != services:
        services = tempServices
        updateService()
    sceneCheck = 1
    threading.Timer(.1,organize).start()

def activeMode():
    if isActive.get():
        for item in sceneList.get(0,END):
            os.popen("taskkill /F /IM "+item)
    threading.Timer(.1,activeMode).start()

if __name__ == "__main__":
    setup()
    organize()
    window.mainloop()
