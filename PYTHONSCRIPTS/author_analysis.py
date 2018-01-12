import io,json
import urllib2,re
import os,sys
import time
import radar as radar

from bs4 import BeautifulSoup as bs
import requests

import numpy as np
import matplotlib.pyplot as plt
from gender import getGenders


def get_author_gender(name):

	"""
	"""

	gender = getGenders(name.split()[0])

	return gender


def gender_check(text):

	"""
	"""

	words = text.split()

	male = ['he','his','He','His']
	female = ['she','her','She','Her']

	n_male = sum(words.count(i) for i in male)
	n_female = sum(words.count(i) for i in female)

	if (n_male>n_female):
		check = 'male'
	elif (n_female>n_male):
		check='female'
	else:
		check='None'

	return check


def get_author_location():

	'''
	'''

	return


def get_author_seniority(text):

	"""
	"""

	words = text.split()

	levels = ['student','Student','postdoc','Postdoc','postdoctoral','fellow','Fellow','researcher','Researcher','Postdoctoral','lecturer','Lecturer','reader','Reader','professor','Professor','Unknown']

	for level in levels:
		if level in words:
			break

	position = level

	if (level=='lecturer'):
		i = words.index('lecturer')
		if (words[i-1]=='senior') or (words[i-1]=='Senior'):
			position = 'Senior Lecturer'
		else:
			position = 'Lecturer'

	elif (level=='Lecturer'):
		i = words.index('Lecturer')
		if (words[i-1]=='senior') or (words[i-1]=='Senior'):
			position = 'Senior Lecturer'
		else:
			position = 'Lecturer'

	if (level=='fellow'): position = 'Postdoctoral'
	if (level=='Fellow'): position = 'Postdoctoral'
	if (level=='postdoctoral'): position = 'Postdoctoral'
	if (level=='Postdoctoral'): position = 'Postdoctoral'
	if (level=='postdoc'): position = 'Postdoctoral'
	if (level=='Postdoc'): position = 'Postdoctoral'

	if (level=='researcher'): 
		i = words.index(level)
		if (words[i-1]=='phd') or (words[i-1]=='PhD'):
			position = 'Student'
		else:		
			position = 'Postdoctoral'

	if (level=='Researcher'): 
		i = words.index(level)
		if (words[i-1]=='phd') or (words[i-1]=='PhD'):
			position = 'Student'
		else:		
			position = 'Postdoctoral'

	if (level=='professor'): 
		i = words.index(level)
		if (words[i-1]=='assistant') or (words[i-1]=='Assistant'):
			position = 'Lecturer'
		elif (words[i-1]=='associate') or (words[i-1]=='Associate'):
			position = 'Reader'
		else:		
			position = 'Professor'

	if (level=='Professor'): 
		i = words.index(level)
		if (words[i-1]=='assistant') or (words[i-1]=='Assistant'):
			position = 'Lecturer'
		elif (words[i-1]=='associate') or (words[i-1]=='Associate'):
			position = 'Reader'
		else:		
			position = 'Professor'

	return position



def update_json():
	# set input data filename:
	inname = "manchester_blogs_tmp.json"

	# read input data from file:
	input_file  = file(inname, "r")
	blogs = json.loads(input_file.read().decode("utf-8-sig"))

	# calculate total number of blog article:
	nblogs = len(blogs)

	# loop through blog articles and update missing fb share counts:
	for i in range(0,nblogs):

		blog = blogs[i]
		
		url = blog['url']
		r = requests.get(url)
		page = r.text
		soup=bs(page,'html.parser')
				
		authors = blog['authors']

		author_genders = []; author_positions = []
		for author in authors:
			gender = get_author_gender(author)
			
			author_boxes = soup.findAll('section',attrs={'class':"author-box"})
			if (author_boxes):
				for box in author_boxes:

					author_name = box.find('span', attrs={'itemprop':"name"}).text
					
					if (author_name==author):
						desc = box.find('div',attrs={'class':"author-box-content"})
						if (desc.p):
							author_desc = desc.p.text

							author_position = get_author_seniority(author_desc)

							check = gender_check(author_desc)
							if (gender[0][0]!=check): 
								if (check=='None') and (gender[0][0]!='None'):
									consensus_gender = gender[0][0]
								elif (check!='None') and (gender[0][0]=='None'):
									consensus_gender = check
								elif (check!='None') and (gender[0][0]!='None'):
									print "True Mismatch"
									print author,gender[0][0],check
							else:
								consensus_gender = gender[0][0]
						else:
							print "No author description for: ",url
						
			author_genders.append(consensus_gender)
			author_positions.append(author_position)

		blogs[i]["gender"] = author_genders
		blogs[i]["position"] = author_positions
			
			
		onwards = raw_input("Hit return")

	# set output data filename:
	ouname = "manchester_blogs_au.json"

	# write the resulting list of post dictionaries to a JSON file with UTF8 encoding:
	with io.open(ouname, 'w', encoding='utf-8') as f:
		f.write(json.dumps(blogs, ensure_ascii=False))


	return




# ==========================================================================================	
# ==========================================================================================	

if __name__ == '__main__':

	update_json()

	# to produce this input file run "update_json"
	filename = "manchester_blogs_au.json"

	input_file  = file(filename, "r")
	blogs = json.loads(input_file.read().decode("utf-8-sig"))

	
	








