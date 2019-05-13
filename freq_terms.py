from gensim import corpora, models
import string
import nltk
from nltk.tokenize import RegexpTokenizer
import os
import sys
import matplotlib.pyplot as plt
import collections
import numpy as np
import json
from POS import POStagFilter

def preprocess(string_txt, language):
	string_txt = string_txt.lower()
	tokenizer = RegexpTokenizer(r'\w+')
	tokens = tokenizer.tokenize(string_txt)
	with open('stop_'+language+'.txt', 'r') as stop_file:
		stop_cont = stop_file.read()
	stops = stop_cont.split()
	filtered_words = [i for i in tokens if i not in stops]
	return filtered_words

def main(argv):
	if(len(sys.argv)!=6):
		print ("Wrong number of parameters: you need the number of terms, the subtitle file, the json file, the language and the POS toggle.")
		sys.exit()
	
	nb_terms = int(sys.argv[1])
	subtitle_file = sys.argv[2]
	json_file = sys.argv[3]
	language = sys.argv[4]
	POStoggle = int(sys.argv[5])
	
	with open(subtitle_file, 'r') as corpus_file:
		docs = corpus_file.readlines()
	
	all_docs = " ".join(docs)
	#POS tagging decision
	
	if(POStoggle == 1):
		all_docs = POStagFilter(all_docs, language)
	else:
		all_docs = preprocess(all_docs, language)
	#print (all_docs)
	#print (docs)
	counter = collections.Counter(all_docs)

	
	m_common = counter.most_common(nb_terms)
	
	comm_terms = [x[0] for x in m_common]
	comm_freq = [int(x[1]) for x in m_common]

	#Uncomment the following and comment the preprocess if you preffer POS tagging
	#docs_list = [nltk.tokenize.word_tokenize(doc, language=language) for doc in docs]
	#Uncomment thie following if you don't use POS tagging
	docs_list = [preprocess(doc, language) for doc in docs]
	distrib = {}
	for term in comm_terms:
		for doc in docs_list:
			try:
				distrib[term].append(doc.count(term))
			except KeyError:
				distrib[term] = [doc.count(term)]
		
	with open(json_file, 'w') as fp:
		json.dump(distrib, fp)
	pass

if __name__ == "__main__":
	main(sys.argv)
