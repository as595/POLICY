import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup as bs
import time

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
	driver = webdriver.Chrome()
	driver.wait = WebDriverWait(driver, 5)
	return driver


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
	box.send_keys(query)
	box.submit()
	time.sleep(5)

	# initial wait for the tweets to load
	wait = WebDriverWait(driver, 10)
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
	
	return page_source


def extract_tweets(page_source):

	soup = bs(page_source,'lxml')
	
	tweets = []
	for li in soup.find_all("li", class_='js-stream-item'):

		# If our li doesn't have a tweet-id, we skip it as it's not going to be a tweet.
		if 'data-item-id' not in li.attrs:
			continue

		tweet = {
			'tweet_id': li['data-item-id'],
			'text': None,
			'user_id': None,
			'user_screen_name': None,
			'user_name': None,
			'created_at': None,
			'retweets': 0,
			'likes': 0
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
		date_span = li.find("span", class_="_timestamp")
		if date_span is not None:
			tweet['created_at'] = float(date_span['data-time-ms'])

		# Tweet Retweets
		retweet_span = li.select("span.ProfileTweet-action--retweet > span.ProfileTweet-actionCount")
		if retweet_span is not None and len(retweet_span) > 0:
			tweet['retweets'] = int(retweet_span[0]['data-tweet-stat-count'])

		# Tweet Likes
		like_span = li.select("span.ProfileTweet-action--favorite > span.ProfileTweet-actionCount")
		if like_span is not None and len(like_span) > 0:
			tweet['likes'] = int(like_span[0]['data-tweet-stat-count'])

		tweets.append(tweet)

	return tweets

def close_driver(driver):

	driver.close()

	return 



if __name__ == "__main__":
	
	driver = init_driver()
	
	username="ammscaife@gmail.com"
	password="Brookf1eld"
	login_twitter(driver, username, password)

	query='http://blog.policy.manchester.ac.uk/posts/2018/01/whats-not-to-like-about-regeneration/'
	page_source = search_twitter(driver, query)
	
	tweets = extract_tweets(page_source)

	close_driver(driver)
