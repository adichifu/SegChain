from nltk.tag import StanfordPOSTagger
import nltk
from nltk.tokenize import RegexpTokenizer

toKeep ={'french': ["V", "NP", "NC", "A"], 'english': ["NN", "NNS", "NNP", "NNP", "NNPS", "JJ", "JJR", "JJS", "VB", "VBD", "VBN", "VBP", "VBZ"]}

def POStagFilter(text, language):
	languageUsed = language
	if(language=='english'):
		languageUsed = language+'-bidirectional-distsim'
	st = StanfordPOSTagger('models/'+languageUsed+'.tagger', 'stanford-postagger.jar', encoding='utf8', java_options='-mx3000m')
	#tagged = st.tag(nltk.tokenize.word_tokenize(text, language=language)) 
	tokenizer = RegexpTokenizer(r'\w+')
	tagged =  st.tag(tokenizer.tokenize(text))
	tokens = [x[0].lower() for x in tagged if x[1] in toKeep[language]]
	with open('stop_'+language+'.txt', 'r') as stop_file:
		stop_cont = stop_file.read()
	stops = stop_cont.split()
	filtered_words = [i for i in tokens if i not in stops]
	return filtered_words

# print (POStagFilter("there's My 3 Suggestions of an edit to fix a deficiency in this answer was rejected. Therefore, please also see my posted answer below which contains some information missing from this answer.", 'english'))
