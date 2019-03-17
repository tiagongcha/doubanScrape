#coding=utf-8
import pymongo
from pymongo import MongoClient
import csv
import sys
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import html.parser

"""connect to MongoDB database
"""
client = MongoClient('mongodb://localhost:27017/')
db = client["movie_database"]
movieCol = db["movie"]
movieCol.delete_many({})
# print(client.list_database_names())
# print(db.list_collection_names())


"""Save to mongoDB
"""
def saveDB(movies_info):
	try:
		movieCol.insert_many(movies_info)
	except Exception as e:
		print("save db error")


"""下载豆瓣选电影页面
	args:
		tag: 不同类型电影，例如：热门，经典，最新等
		sort: 按什么排序，可以是热度，时间，或者凭借
	return:
		selenium webdriver object reference
"""
def getPage(tag, sort):
	url = "https://movie.douban.com/explore#!type=movie&tag=" + tag + "sort=" + sort + "&page_limit=20&page_start=0" 
	# default browser: chrome
	driver = webdriver.Chrome('/Users/gongtia/Desktop/tiagongcha/cs6015/movieFinder/chromedriver')
	driver.get(url) 
	return driver

"""点击进入每一部电影自己的页面，爬去更多关于一部电影的信息
	args:
		driver: selenium webdriver object reference
		url: 一部电影自己的豆瓣链接
	return:
		tuples of 电影名称，年份，和评价人数
"""
def stepInHref(driver, url):
	driver.get(url)
	response = driver.page_source
	soup = BeautifulSoup(response, "html.parser")
	title = soup.find('h1')
	name = title.find_all('span')[0].get_text()
	year = title.find_all('span')[1].get_text()
	# trim the year string:
	year = year[year.find("(")+1:year.find(")")]
	ratingNum = soup.find('a', class_ = 'rating_people').find('span').get_text()
	# return back to the main 选电影页面
	driver.back()
	return name, year, ratingNum

"""用beautifulsoup爬去选择的tag下面所以电影的信息
	args:
		tag: 5不同类型电影，例如：热门，经典，最新等
		sort: 按什么排序，可以是热度，时间，或者凭借
		pagenum：每一页豆瓣选电影界面有20个电影，这个pagenum用来设定用户想要多少页面 如果pagenum = 5 那么一共会抓去 5*20部电影
		writer: csv file writer object reference
"""
def movie_spider(tag, sort, pageNum, writer, movies_info):
	#get the main url of the webpage
	driver = getPage(tag, sort)
	#since the webpage html loaded asynchronously with javascript, everytime click "loadmore", we send ajex request to 
	#the page update portions of 20 movies' content without having to refresh the page
	for i in range(pageNum):
		# send the page to sleep 30s to avoid racing situation
		time.sleep(30) 	
		driver.find_element_by_partial_link_text("加载更多").click()
	response = driver.page_source
	soup = BeautifulSoup(response, "html.parser")

	for hit in soup.find_all('a', class_='item'):
		entry = []
		score = hit.find('p').find('strong').get_text()
		link = hit.get('href')
		name, year, ratingNum = stepInHref(driver, link)
		
		entry.append(name)
		entry.append(year)
		entry.append(score)
		entry.append(ratingNum)
		entry.append(link)

		# create dictionary to save to database:
		dict = {"name" : name, "year": year, "score" : score, "num" : ratingNum, "link" : link}
		movies_info.append(dict)

		#write row to csv file
		try:
			writer.writerow(entry)
		except csv.Error as e:
			sys.exit(1)

def main():
	writer = csv.writer(open('movies.csv', 'w', newline='', encoding='utf-8'))
	fields = ('电影名', '年份', '评分', '评价人数' ,'豆瓣链接')
	writer.writerow(fields)
	movies_info = []
	movie_spider("热门", 'time', 1, writer, movies_info)
	
	saveDB(movies_info)

if __name__ == '__main__':
    main()





















