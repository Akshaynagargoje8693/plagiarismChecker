from django.shortcuts import render
from django.http import HttpResponse
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings


def home(request):
    return render(request,'homepage/homepage.html')


def login(request):
    return render(request, 'login/login.html')


superUsername="" 


def loginLogic(request):
    found=0 
    logindatabase=open('userdatabase.txt') 
    global superUsername 
    loginbuffer=request.POST['username']+'|'+request.POST['password'] 
    superUsername=request.POST['username']
    for user in logindatabase:
        if user.strip()==loginbuffer: 
            found=1 
    LoginDict={ 
    'username':superUsername,
    }
    if(found==1):
        return render(request, 'plagiarism/plagiarism.html',LoginDict) 
    else:
        return render(request, 'login/wrongLogin.html') 


def register(request):
    return render(request, 'register/register.html')


def registerlogic(request):
    found=0  
    logindatabase=open('userdatabase.txt','r') 
    registerusername=request.POST['username'] 
    registerbuffer=request.POST['username']+'|'+request.POST['password']+'\n' 
    for user in logindatabase: 
        userlist=user.split('|') 
        if userlist[0]==registerusername:  
            found=1 
    logindatabase.close()
    if(found==1):  
        return render(request, 'register/wrongRegister.html')
    else: 
        logindatabase=open('userdatabase.txt','a')
        logindatabase.write(registerbuffer)
        return render(request, 'login/registerSucess.html') 

superFile=None 
superList=[]

def plagiarismRender(request):
    if superUsername == "":
        return render(request, 'login/login.html')
    else:
        LoginDict={ 
        'username':superUsername,
        }
        return render(request, 'plagiarism/plagiarism.html',LoginDict)
def postUpload(request):
    
    global superFile
    global superList
    file = request.FILES['sentFile'] 
    superFile=file.name 

    
    path = default_storage.save(f'bufferFolder/{file.name}', ContentFile(file.read()))
    tmp_file = os.path.join(settings.MEDIA_ROOT, path)
    file=open(f'bufferFolder/{file.name}') 

    bufferlines=[] 

    for line in file:
        superList.append(line) 
        sentences=line.split('.') 
        bufferlines.extend(sentences)
    file.close()
    os.remove(f'{file.name}') 
    bufferlinewords=[] 
    for line in bufferlines:  
        bufferwords=line.split(' ') 
        if(bufferwords!=['\n']): 
            bufferlinewords.append(bufferwords) 
    for linewords in bufferlinewords: 
        if len(linewords)<=3: 
            bufferlinewords.remove(linewords)
    LineCheck=[] 
    LineCount=len(bufferlinewords) 
    for i in range(LineCount): 
        LineCheck.append(0)
    directory='fileDatabase' 
    OutputList=[] 
    for filename in os.listdir(directory): 
        file=open(f'fileDatabase/{filename}') 
        bufferlines=[] 
        for line in file:
            sentences=line.split('.')
            bufferlines.extend(sentences)
        file.close()
        destBufferlinewords=[]
        for line in bufferlines:
            bufferwords=line.split(' ')
            if(bufferwords!=['\n']):
                destBufferlinewords.append(bufferwords)
        for linewords in destBufferlinewords:
            if len(linewords)<=3:
                destBufferlinewords.remove(linewords)
        allCount=0 
        allTotal=0 
        print("1")
        for eachline in bufferlinewords: 
            OutputContentList = []
            matched = False
            allTotal+=1 
            for destEachline in destBufferlinewords: 
                count=0 
                total=0 
                for eachword in eachline:
                    total+=1 
                    if eachword in destEachline: 
                        count+=1
                if (count/total)>=.80: 
                    print('matched')
                    matched = True
                    allCount+=1 
                    LineCheck[allTotal-1]=1 
                    break 
            print("eachline")
            print(matched)
            if (matched):
                OutputContentList.append(eachline)
            print(eachline)                    
        if(allTotal!=0):
            percentPlag=allCount/allTotal*100 
            OutputList.append(f"The Percentage Plagiarism from {filename} is %.2f"%percentPlag) 

    FinalPlagCount=0 
    for each in LineCheck: 
        if each==1:
            FinalPlagCount+=1
    FinalOutput="NULL"
    if(LineCount!=0):
        OverallPercentPlag=FinalPlagCount/LineCount*100 
        FinalOutput=(f"The Overall Percentage Plagiarism is %.2f"%OverallPercentPlag) 
    else:
        FinalOutput=f"Your File {superFile} is empty "
    OutputDict={  
    "OutputList":OutputList,
    "OutputContentList":OutputContentList,
    "FinalOutput":FinalOutput,
    }
    return render(request,"plagiarism/plagiarismOutput.html",OutputDict) 


def addFile(request):
    OutputStatement={
    'username':superUsername,
    'filename':superFile,
    }
    if(request.POST['include']=='YES'): 
        filename=superUsername+"'s "+str(superFile) 
        file=open(f'fileDatabase/{filename}','a') 
        for line in superList: 
            file.write(line) 
        return render(request,'FinalPage/FileAdded.html',OutputStatement) 
    else:

        return render(request,'FinalPage/ThankYou.html',OutputStatement) 

def uploadMultipleFilesRender(request):
    directory='fileDatabase'
    fileArray = [] 
    for filename in os.listdir(directory): 
        fileArray.append(filename)
    fileArr={
        'fileArray':fileArray
    }
    return render(request, 'uploadFiles/uploadFiles.html',fileArr)

def uploadMultipleFiles(request):
    
    global superFile
    global superList
    print(request.FILES.getlist('sentFile'))
    for f in request.FILES.getlist('sentFile'):
        superFile = f.name
        OutputStatement={
        'username':superUsername,
        'filename':superFile,
        }
        filename=superUsername+"'s "+str(superFile) 
        file=open(f'fileDatabase/{filename}','a') 
        for line in superList: 
            file.write(line) 
    return render(request,'FinalPage/FileAdded.html',OutputStatement) 