#Import modules
import json
import sys
# import matplotlib.pyplot as plt
# from matplotlib.pyplot import cm 
import collections
import numpy as np
from numpy import inf
import json
from scipy import spatial
from scipy import stats
from scipy import misc
import scipy.fftpack as scfft
from scipy.signal import argrelextrema
from scipy.signal import argrelmin
import statistics
import warnings
import pysubs2
import datetime
from datetime import datetime
import xml.etree.cElementTree as ET


#Ignore warnings due to "nan" values in cosine vector
warnings.filterwarnings("ignore")

#Function to sum elements between two list positions
def aggr_list(list, pos_list, start, end):
	man = [0 for x in range(pos_list[-1])]
	for position in list:
		man[position] = 1
	return sum(man[pos_list[start]:pos_list[end]])/(pos_list[end] - pos_list[start])

#The main function
def main(argv):
	if(len(sys.argv)!=8):
		print ("Wrong number of parameters: you need [the number of terms], [the json data file], [the basename for the graphs], [the subtitle file], [the output_file], [the factor of terms to remove] and [the factor for local minimum order]as parameters.")
		sys.exit()
	
	#Read command-line parameters
	N = int(sys.argv[1])
	json_file = sys.argv[2]
	basename_graphs = sys.argv[3]
	subtitle_file = sys.argv[4]
	output_file = sys.argv[5]
	removeTermsFactor = float(sys.argv[6])
	minFactor = float(sys.argv[7])
	
	#oFile = open(output_file, 'w')
	
	with open(json_file, 'r') as fp:
	    distrib = json.load(fp)
	fp.close()
	
	#Sort the keys (first is the most occurring)
	keys = sorted(distrib, key=lambda k: sum(distrib[k]), reverse=True)
	
	#Initialize data structures:
	# - non0: positions for occurring keys along the subtitle
	non0 = {}
	
	# - non0C: positions for chains of occurring keys along the subtitle
	non0C = {}
	hiatus = {}
	
	# - 
	chainNb = {}
	pointsNb = {}
	matrix = {}
	weighDist = {}
	non0C_json = {}
	zonePresence = {}
	keys = keys[0:N]
	lengthX = len(distrib[keys[0]])
	
	for key in keys:
		chainNb[key] = 1

	continuu = 0

	for key in keys:
		non0[key] = list(np.nonzero(distrib[key])[0])
		pointsNb[key] = len(non0[key])
		non0C[key] = non0[key].copy()
		size = len(non0C[key])
		hiatus[key] = (non0C[key][size-1]-non0C[key][0])/(size-1)
		
		inserted = 0
		
		for i in range(0,size-1):
			dist = non0C[key][i+inserted+1]-non0C[key][i+inserted]
			if dist <= hiatus[key]:
				for j in range(1,dist):
					non0C[key].insert(i+inserted+j,non0C[key][i+inserted]+j)
				inserted +=dist-1
		for x in range(len(non0C[key])-1):
			if non0C[key][x]+1 != non0C[key][x+1]:
				chainNb[key] += 1 
		
		matrix[key] = [0] * lengthX
		
		for pos in non0C[key]:
			matrix[key][pos] = 1
	for key in keys:
		weighDist[key] = pointsNb[key]/(((non0C[key][len(non0C[key])-1]-non0C[key][0])/lengthX)*chainNb[key]/max(chainNb.values()))
	
	keys = sorted(weighDist, key=weighDist.get, reverse=True)
	
	oldN = N
	N = int(N - (N*removeTermsFactor))
	
	cos = [[0.0 for x in range(N)] for x in range(N)] 
	for i in range(0,N):
		for j in range(0,N):
			if i != j:
				cos[i][j] = 1 - spatial.distance.cosine(matrix[keys[i]], matrix[keys[j]])
			else:
				cos[i][j] = 1.0


	lengthTime = len(matrix[keys[0]])
	timeline = [[0.0 for x in range(N)] for x in range(lengthTime)] 

	for i in range(lengthTime):
		for j in range(N):
			timeline[i][j] = int(matrix[keys[j]][i])

	simCos = [0.0 for x in range(lengthTime-1)]

	for i in range(lengthTime-1):
		#simCos[i] = 1 - float(spatial.distance.cosine(timeline[i], timeline[i+1]))
		simCos[i] = 1 - float(spatial.distance.hamming(timeline[i], timeline[i+1]))
	
	array_simCos = np.array(simCos)
	loc_min = argrelmin(array_simCos, order=int(lengthX*minFactor+1), mode='clip')[0]
	bloc_min = list(loc_min.copy())
	bloc_min.append(lengthX)
	bloc_min.insert(0,0)
	
	mat_zone = {}
	
	for key in range(0,N):
		mat_zone[keys[key]] = [0]*(len(bloc_min)-1)
		cnt = 0
		for pos in range(len(bloc_min)-1):
			mat_zone[keys[key]][cnt] = aggr_list(non0C[keys[key]], bloc_min, pos, pos+1)
			cnt += 1
	
	lengthZone = len(mat_zone[keys[0]])
	zone_line = [[0.0 for x in range(N)] for x in range(lengthZone)] 
	
	for i in range(lengthZone):
		for j in range(N):
			zone_line[i][j] = float(mat_zone[keys[j]][i])
	
	cosZone = [0.0 for x in range(lengthZone-1)]

	for i in range(lengthZone-1):
		cosZone[i] = 1 - float(spatial.distance.cosine(zone_line[i], zone_line[i+1]))
	
	del bloc_min[0]
	zone2keep = []
	for i in range(lengthZone-1):
		if (cosZone[i]<=0.6):
			zone2keep.append(i)
	
	finalZone = []
	for zone in zone2keep:
		finalZone.append(bloc_min[zone])
	
	subs = pysubs2.load(subtitle_file, encoding="utf-8")
	
	segments = ET.Element("segments")
	
	id = 0
	finalZone.insert(0, 0)
	finalZone.append(lengthX-1)
	
	finalZoneC = finalZone.copy()
	del finalZoneC[-1]
	finalZoneC.append(lengthX)
	
	
	
	for i in range(0,N):
		zonePresence[keys[i]] = [0.0 for x in range(len(finalZoneC)-1)]
	
	for pos in range(1,len(finalZoneC)):
		start = finalZoneC[pos-1]
		end = finalZoneC[pos]
		for i in range(0,N):
			man = [0 for x in range(lengthX)]
			for position in non0C[keys[i]]:
				man[position] = 1
			zonePresence[keys[i]][pos-1] = round(sum(man[start:end+1])/((end-start+1)),2)
	
	for i in range(1,len(finalZone)):
		segment = ET.SubElement(segments, 'segment')
		segment.set('id',str(id))
		
		subID = ET.SubElement(segment, 'subID')
		subID.text = str(finalZone[i])
		
		timeBegin = ET.SubElement(segment, 'timeBegin')
		timeBegin.text = datetime.utcfromtimestamp(float(subs[finalZone[i-1]].start/1000)).strftime('%H:%M:%S,%f')[:-3]
		
		timeEnd = ET.SubElement(segment, 'timeEnd')
		timeEnd.text = datetime.utcfromtimestamp(float(subs[finalZone[i]].start/1000)).strftime('%H:%M:%S,%f')[:-3]
		
		man = {}
		
		keywords = ET.SubElement(segment, 'keywords')
		
		for j in range(0,N):
			if(zonePresence[keys[j]][i-1] != 0):
				man[keys[j]] = zonePresence[keys[j]][i-1]
		keys1 = sorted(man, key=man.get, reverse=True)
		
		
		for k in range(len(keys1)):
			keyword = ET.SubElement(keywords, 'keyword')
			keyword.set('score', str(man[keys1[k]]))
			keyword.text = keys1[k]
		
		id += 1
	
	tree = ET.ElementTree(segments)
	tree.write(output_file, encoding="utf8", xml_declaration=None, default_namespace=None, method="xml")
	
	pass

if __name__ == "__main__":
	main(sys.argv)
