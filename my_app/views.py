from pydoc import doc
from xml.dom.minidom import Document
from django.shortcuts import render
from django.http import HttpResponse
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from scholarly import scholarly
from googlesearch import search
import requests
from bs4 import BeautifulSoup
from rake_nltk import Rake
import json

def home(request):
    return render(request,'homepage/homepage.html')


def login(request):
    return render(request, 'login/login.html')

    

superUsername="" 


def logout(request):
    superUsername=''
    return render(request,'login/login.html')

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

  
def checkPlagiarism(request):
    compareType = request.POST['compareType']
    if(compareType == 'Online'):
        return compareOnline(request)
    if(compareType == 'FileDB'):
        return postUpload(request)


def postUpload(request):
    print("request",request.POST['compareType'])
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
    OutputContentList = []
    
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
        # print("1")
        OutputContentList1 = []
        
        for eachline in bufferlinewords: 
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
                    # print('matched')
                    matched = True
                    allCount+=1 
                    LineCheck[allTotal-1]=1 
                    break 
            # print("eachline")
            # print(matched)
            if (matched):
                OutputContentList1.append(eachline)
            # print(eachline)                    
        if(allTotal!=0):
            OutputContentList.append({"filename":filename,"content":OutputContentList1})
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
    "OutputContentList":json.dumps(OutputContentList),
    "FinalOutput":FinalOutput,
    }
    print("FinalOutput",json.dumps(OutputContentList))
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

def getGoogleDocText(textURL='https://docs.google.com/document/d/e/2PACX-1vSJLCQ0NCFsy5di5oR5deO8L_hnWLpcwN0IlDrFfqMLwawMrn-wH5KUVaKHemW80b_UGudFJyK6mXw9/pub'):
    
    print('Checking URL for text...')
    html = requests.get(textURL).text
    beautifulCleaner = BeautifulSoup(html, 'lxml')
    cleanedText = beautifulCleaner.find_all('p')
    paragraphList = []
    for i in cleanedText:
        if len(i.text) > 0:
            paragraphList.append(i.text)
    print(str(len(paragraphList)) + ' paragraphs identified')
    return paragraphList



def checkForExactMatches(paragraph='Guillermo Alberto Santiago Lasso Mendoza (born 16 November 1955) is an Ecuadorian businessman and politician'):
    
    print('Checking Google for exact matches with paragraph beginning...' + paragraph[:28])
    results_list = []
    for i in search('"' + paragraph + '"', num=5, start=0, stop=5, pause=2): 
        results_list.append(i)
    print(str(len(results_list)) + ' potential matches found.')
    return results_list

def docCheck(paragraphList):
    
    resultsByParagraph = []
    for para in paragraphList:
        resultsByParagraph.append([para, checkForExactMatches(para)])
    return resultsByParagraph



def extractKeywordsFromParagraph(paragraph, maxKeyTerms=3):
    
    print('Searching for keywords in paragraph beginning... ' + paragraph[:28])
    print("0")
    r = Rake(min_length=1, max_length=5)
    print("1")
    r.extract_keywords_from_text(paragraph)
    print("2")
    phraseList = r.get_ranked_phrases()
    if len(phraseList) > 0:
        print('Keywords found: ' + str(phraseList[:maxKeyTerms]))
        return phraseList[:maxKeyTerms]
    else:
        return []

def googleScholarSearch(paragraphList=[]):
    
    print('Checking for Google Scholar sources based on paragraph keywords...')
    sourcesByKeyWordByParagraph = []
    if len(paragraphList) > 0:
        for para in paragraphList:
            print('For paragraph starting: ' + para[:28])
            kwList = extractKeywordsFromParagraph(para)
            sourceList = []
            if len(kwList) > 0:
                for keyWord in kwList:
                    search_query = scholarly.search_pubs(keyWord)
                    this = next(search_query)
                    sourceList.append([keyWord, this['bib'], this['pub_url']])
                    print('Based on keyword: ' + keyWord + ' the following article identified: ')
                    print(this['bib']['title'])
            sourcesByKeyWordByParagraph.append([para, sourceList])
    return sourcesByKeyWordByParagraph

def compareOnline(request):
    print("request",request.POST['compareType'])
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
    finalSentanceList = [];
    for sent in bufferlines:
        if(sent != '\n' and sent!= ''):
            finalSentanceList.append(sent)
    # print('aaaaaaaaaaa',finalSentanceList)
    listOfPossiblePlagarizedSources = docCheck(finalSentanceList)
    # listOfPossibleSources = googleScholarSearch(finalSentanceList)
    # print("online result1",listOfPossiblePlagarizedSources)
    finalArr = []
    for list in listOfPossiblePlagarizedSources:
        obj = {
            "sentance": list[0],
            "urls": list[1]
        }
        finalArr.append(obj)
    # print("online result2",listOfPossibleSources)
    fileArr={
        'OutputList':finalArr
    }
    print("finalArr",finalArr)
    return render(request, 'plagiarism/onlinePlagiarismOutput.html',fileArr)
# listOfParagraphs = getGoogleDocText()

# listOfPossiblePlagarizedSources = docCheck(listOfParagraphs)

# listOfPossibleSources = googleScholarSearch(listOfParagraphs)
