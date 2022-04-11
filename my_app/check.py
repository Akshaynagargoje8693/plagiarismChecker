from cosineSim import *
from googlesearch import search
from bs4 import BeautifulSoup
from htmlstrip import *

# from htmlstrip import *
# from extractdocx import *

#import required modules
import codecs
import traceback
import sys
import operator
import urllib.parse
import urllib.request
import json as simplejson
import requests
# Given a text string, remove all non-alphanumeric
# characters (using Unicode definition of alphanumeric).
def getQueries(text,n):
	import re
	sentenceEnders = re.compile('[.!?]')
	sentenceList = sentenceEnders.split(text)
	sentencesplits = []
	for sentence in sentenceList:
		x = re.compile(r'\W+', re.UNICODE).split(sentence)
		x = [ele for ele in x if ele != '']
		sentencesplits.append(x)
	finalq = []
	for sentence in sentencesplits:
		l = len(sentence)
		l=l/n
		index = 0
		print(sentence)
		for i in range(0,1):
			print("1")
			finalq.append(sentence[index:index+n])
			index = index + n-1
		if index !=len(sentence):
			finalq.append(sentence[len(sentence)-index:len(sentence)])
	return finalq

# Search the web for the plagiarised text
# Calculate the cosineSimilarity of the given query vs matched content on google
# This is returned as 2 dictionaries 
def searchWeb(text,output,c):
	try:
		text = text.encode('utf-8')
	except:
		text =  text
	query = urllib.parse.quote_plus(text)
	if len(query)>60:
		return output,c
	#using googleapis for searching web
	# response = search(query, tld="co.in", num=10, stop=10, pause=2)
	# print("2")
	# print(response)
	# for j in search(query, tld="co.in", num=10, stop=10, pause=2):
		# print(j)
	# base_url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q='
	# url = base_url + '%22' + query + '%22'
	# print(url)
	# request = urllib.request.Request(url)
	# print(request);
	# response = urllib.request.urlopen(request)
	# print("21")
	# results = simplejson.load(response)
	try:
			for ele in search(query, tld="co.in", num=10, stop=10, pause=2):
				print("001")	
				r = requests.get(ele)
				soup = BeautifulSoup(r.content, 'html5lib') # If this line causes an error, run 'pip install html5lib' or install html5lib
				# print(soup.prettify())
				# print(r.content)
				Match = ele
				# Match = results['responseData']['results'][0]
				content = r.content
				print(output)
				print("-----")
				print(Match)
				if Match in output:
					print("inside if")
				    #print text
					print(strip_tags(content))
					output[Match] = output[Match] + 1
					c[Match] = (c[Match]*(output[Match] - 1) + cosineSim(text,strip_tags(content)))/(output[Match])
				else:
					print('in else')
					print('text',text);
					# print()
					output[Match] = 1
					c[Match] = cosineSim(text,strip_tags(content))
	except Exception as e:
		print('in except')
		print(e)
		return output,c
	return output,c
    

# Use the main function to scrutinize a file for
# plagiarism
def main():
    	# n-grams N VALUE SET HERE
	n=9
	queries = getQueries(' this is my first program',n)
	q = [' '.join(d) for d in queries]
	found = []
	#using 2 dictionaries: c and output
	#output is used to store the url as key and number of occurences of that url in different searches as value
	#c is used to store url as key and sum of all the cosine similarities of all matches as value	
	output = {}
	c = {}
	i=1
	count = len(q)
	print(count)
	if count>100:
		count=100
	for s in q[:100]:
		output,c=searchWeb(s,output,c)
		msg = "\r"+str(i)+"/"+str(count)+"completed..."
		print(msg)
		print(output,c)
		i=i+1
  

main()