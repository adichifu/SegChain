import lxml.etree as elm
import sys
import codecs
import re
import datetime
from datetime import datetime

def strip_tags(value):
    """Returns the given HTML with all tags stripped."""
    return ' '.join(re.compile(r'<[^<]*?/?>').sub('', value).split())

def main(argv):
	if(len(sys.argv)!=3):
		print ("Wrong number of parameters: you need [the trs input file] and [the srt output file] as parameters.") 
		sys.exit()
		
	subFile = sys.argv[1]
	srtFile = sys.argv[2]
	#targetFile = codecs.open(subFile,mode='r',encoding='utf-8')
	parser = elm.XMLParser(recover=True) # recover from bad characters.
	e = elm.parse(subFile, parser=parser).getroot()
	#print (elm.tostring(e))

	count = 0;
	
	outFile = open(srtFile, "w")

	
	for episode in e.findall('Episode'):
		for section in episode.findall('Section'):
			for turn in section.findall('Turn'):
				start = datetime.utcfromtimestamp(float(turn.get('startTime')))
				end = datetime.utcfromtimestamp(float(turn.get('endTime')))
				text = strip_tags(elm.tostring(turn,encoding='UTF-8').decode("utf8").replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", ""))
				outFile.write(str(count)+"\n"+start.strftime('%H:%M:%S,%f')[:-3]+" --> "+end.strftime('%H:%M:%S,%f')[:-3]+"\n"+text+"\n\n\n")
				count += 1
	outFile.close()
	pass

if __name__ == "__main__":
	main(sys.argv)