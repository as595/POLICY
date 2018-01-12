import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup as bs
import time
import json,io
from datetime import datetime



class wait_for_more_than_n_elements_to_be_present(object):
    def __init__(self, locator, count):
        self.locator = locator
        self.count = count

    def __call__(self, driver):
        try:
            elements = EC._find_elements(driver, self.locator)
            return len(elements) > self.count
        except StaleElementReferenceException:
            return False


def init_driver():
	# duh... got to have chrome installed as well as chromedriver!
	#chromedriver='/usr/local/bin/chromedriver'
	#options = webdriver.ChromeOptions()
	#driver = webdriver.Chrome(chromedriver,chrome_options=options)
	driver = webdriver.Chrome()
	driver.wait = WebDriverWait(driver, 5)
	return driver


def close_driver(driver):

	driver.close()

	return 


def login_twitter(driver, username, password):

	driver.get("https://twitter.com/login")

	username_field = driver.find_element_by_class_name("js-username-field")
	password_field = driver.find_element_by_class_name("js-password-field")

	username_field.send_keys(username)
	driver.implicitly_wait(1)
    
	password_field.send_keys(password)
	driver.implicitly_wait(1)

	driver.find_element_by_class_name("EdgeButtom--medium").click()

	return


def search_twitter(driver, query):
	
	box = driver.wait.until(EC.presence_of_element_located((By.NAME, "q")))
	driver.find_element_by_name("q").clear()
	box.send_keys(query)
	box.submit()
	time.sleep(5)

	# initial wait for the tweets to load
	wait = WebDriverWait(driver, 10)
	try:
		wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "li[data-item-id]")))

		# scroll down to the last tweet until there is no more tweets loaded
		while True:
			tweets = driver.find_elements_by_css_selector("li[data-item-id]")
			number_of_tweets = len(tweets)

			driver.execute_script("arguments[0].scrollIntoView();", tweets[-1])

			try:
				wait.until(wait_for_more_than_n_elements_to_be_present((By.CSS_SELECTOR, "li[data-item-id]"), number_of_tweets))

			except TimeoutException:
				break

		page_source = driver.page_source
		
	except TimeoutException:
		page_source=None


	return page_source



def compile_info(tweets):

	# initiate everything to zero:
	total_tweets = 0; total_likes = 0; total_replies = 0

	if tweets is not None:
		for tweet in tweets:

			# retweets plus one to include original tweet:
			total_tweets += tweet["retweets"] + 1
			total_likes += tweet["likes"]
			total_replies += tweet["replies"]


	return total_tweets, total_likes, total_replies



def extract_tweets(page_source):

	soup = bs(page_source,'lxml')
	
	tweets = []
	for li in soup.find_all("li", class_='js-stream-item'):

		# If our li doesn't have a tweet-id, we skip it as it's not going to be a tweet.
		if 'data-item-id' not in li.attrs:
			continue

		else:
			tweet = {
				'tweet_id': li['data-item-id'],
				'text': None,
				'user_id': None,
				'user_screen_name': None,
				'user_name': None,
				'created_at': None,
				'retweets': 0,
				'likes': 0,
				'replies': 0
			}

			# Tweet Text
			text_p = li.find("p", class_="tweet-text")
			if text_p is not None:
				tweet['text'] = text_p.get_text()

			# Tweet User ID, User Screen Name, User Name
			user_details_div = li.find("div", class_="tweet")
			if user_details_div is not None:
				tweet['user_id'] = user_details_div['data-user-id']
				tweet['user_screen_name'] = user_details_div['data-screen-name']
				tweet['user_name'] = user_details_div['data-name']

			# Tweet date
			date_span = li.find("a", class_="tweet-timestamp")
			if date_span is not None:
				tweet['created_at'] = str(date_span['title'])

			# Tweet Retweets
			retweet_span = li.select("span.ProfileTweet-action--retweet > span.ProfileTweet-actionCount")
			if retweet_span is not None and len(retweet_span) > 0:
				tweet['retweets'] = int(retweet_span[0]['data-tweet-stat-count'])

			# Tweet Likes
			like_span = li.select("span.ProfileTweet-action--favorite > span.ProfileTweet-actionCount")
			if like_span is not None and len(like_span) > 0:
				tweet['likes'] = int(like_span[0]['data-tweet-stat-count'])

			# Tweet Replies
			reply_span = li.select("span.ProfileTweet-action--reply > span.ProfileTweet-actionCount")
			if reply_span is not None and len(reply_span) > 0:
				tweet['replies'] = int(reply_span[0]['data-tweet-stat-count'])


			if (tweet['text'].find("blog.policy.manchester")>=0):
				tweets.append(tweet)

	return tweets


def query_twitter(driver, query):

	page_source = search_twitter(driver, query)
	
	if page_source is not None:
		tweets = extract_tweets(page_source)
	else:
		tweets = None

	return tweets
		


def check_dates(tweets,date):

	blog_date = datetime.strptime(date,'%B %d, %Y')
	bad_list=[]
	
	i = 0
	while True:

		if (i>=len(tweets)): break

		tweet_date = datetime.strptime(tweets[i]['created_at'], '%I:%M %p - %d %b %Y')
		diff = (blog_date - tweet_date).total_seconds()
		if diff > 0. :
			print "Removing...", tweets[i]
			tweets.pop(i)
		else:
			i+=1

	
	return tweets



def check_url(tweets):

	i = 0
	while True:

		if (i>=len(tweets)): break
		
		if tweets[i]['text'].find("blog.policy.manchester") < 0 :
			tweets.pop(i)
		else:
			i+=1

	
	return tweets




def scrape_twitter(driver,blogs):

	# calculate total number of blog article:
	nblogs = len(blogs)

	# loop through blog articles and update missing fb share counts:
	for i in range(0,nblogs):

		blog = blogs[i]
		
		url = blog['url']
		title = blog['title']
		date = blog['date']
		cats = blog['categories']


		# first query the title:
		tweets = query_twitter(driver, title)
		
		# check date range:
		if tweets is not None:
			tweets = check_dates(tweets, date)

		# check for url in text:
		if tweets is not None:
			tweets = check_url(tweets)

		# then query the url directly:
		if tweets is not None:
			tweets += query_twitter(driver, url)
		else:
			tweets = query_twitter(driver, url)

		
		# check for duplicates:
		if tweets is not None:
			tweets = [t for n,t in enumerate(tweets) if t not in tweets[:n]]

		print title
		print tweets

		total_tweets, total_likes, total_replies = compile_info(tweets)

		blogs[i]['twitter'] = {
			'tweets': 0,
			'likes': 0,
			'replies': 0
		}

		blogs[i]['twitter']['tweets'] = total_tweets
		blogs[i]['twitter']['likes'] = total_likes
		blogs[i]['twitter']['replies'] = total_replies
		
		#onwards = raw_input("Hit return")


	return blogs



if __name__ == "__main__":
	
	driver = init_driver()

	login_twitter(driver, username, password)

	# set input data filename:
	inname = "../DATA/manchester_blogs_tmp.json"

	# read input data from file:
	input_file  = file(inname, "r")
	blogs = json.loads(input_file.read().decode("utf-8-sig"))

	blogs = scrape_twitter(driver,blogs)

	# set output data filename:
	ouname = "manchester_blogs_tw.json"

	# write the resulting list of post dictionaries to a JSON file with UTF8 encoding:
	with io.open(ouname, 'w', encoding='utf-8') as f:
	  f.write(json.dumps(blogs, ensure_ascii=False))

	
	close_driver(driver)
