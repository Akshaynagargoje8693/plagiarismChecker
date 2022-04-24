from scholarly import scholarly
from googlesearch import search
import requests
from bs4 import BeautifulSoup
from rake_nltk import Rake


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




listOfParagraphs = getGoogleDocText()

listOfPossiblePlagarizedSources = docCheck(listOfParagraphs)

listOfPossibleSources = googleScholarSearch(listOfParagraphs)

print('Full list of paragraphs...')
print(listOfParagraphs)
print('Full list of possible plagiarized sources from Google...')
print(listOfPossiblePlagarizedSources)
print('Full list of possible sources from Google Scholar...')
print(listOfPossibleSources)