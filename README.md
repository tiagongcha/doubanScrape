# 豆瓣选电影爬虫

简单的选电影爬虫，基本url为：https://movie.douban.com/explore#!type=movie&tag=%E7%83%AD%E9%97%A8&sort=rank&page_limit=20&page_start=0

- client自行选取选电影标签（例如热门，悬疑等， 和按什么条件排序（例如按热度，时间，评价）
- 豆瓣用ajax加载内容，这里用了selenium来处理，并没有用json
- 爬取到的数据储存在mongodb，以及一份csv文件




