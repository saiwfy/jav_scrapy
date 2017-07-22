# -*- coding: utf-8 -*-
import scrapy
import codecs
import sys

import re

reload(sys)
sys.setdefaultencoding('utf-8')

class JavbusSpider(scrapy.Spider):
	name = 'javbus'
	allowed_domains = ['javbus.com']
	start_urls = [
		'https://www.javbus.com/genre/30',
		#'https://www.javbus.com/AP-447'
	]

	def parse(self, response):

		for sel in response.css('#waterfall > div '):
			link = sel.css('a::attr(href)').extract();
			yield response.follow(link[0],self.parse_detail)
		# 测试抓单条
		#yield response.follow("https://www.javbus.com/STAR-800",callback = self.parse_detail)

		#翻页
		# pagenation = response.css('#next::attr(href)').extract_first()
		# if pagenation is not None:
		# 	yield response.follow(pagenation,self.parse)

	def parse_detail(self,response):


		def extract_with_css(query):
			if response.css(query).extract_first() is not None:
				return response.css(query).extract_first().strip()

		

		#提取页面本身有的元素
		title = extract_with_css('body > div.container > h3::text')
		#actor = ",".join(response.css('#star_r0n > li > div > a::text').extract())
		code = extract_with_css('body > div.container > div.row.movie > div.col-md-3.info > p:nth-child(1) > span:nth-child(2)::text')
		publish_date = extract_with_css('body > div.container > div.row.movie > div.col-md-3.info > p:nth-child(2)::text')
		tag_count = 2
		actor_count = 5
		if response.body.find('識別碼:') > 0:
			tag_count = tag_count+1
			actor_count = actor_count+1
		if response.body.find('發行日期:') > 0:
			tag_count = tag_count+1
			actor_count = actor_count+1
		if response.body.find('長度:') > 0:
			tag_count = tag_count+1
			actor_count = actor_count+1
		if response.body.find('製作商:') > 0:
			tag_count = tag_count+1
			actor_count = actor_count+1
		if response.body.find('系列:') > 0:
			tag_count = tag_count+1
			actor_count = actor_count+1
		if response.body.find('導演:') > 0:
			tag_count = tag_count+1
			actor_count = actor_count+1
		if response.body.find('發行商:') > 0:
			tag_count = tag_count+1
			actor_count = actor_count+1

		actor = ",".join(response.css('body > div.container > div.row.movie > div.col-md-3.info > p:nth-child('+str(actor_count)+') > span > a::text').extract())
		tag = ",".join(response.css('body > div.container > div.row.movie > div.col-md-3.info > p:nth-child('+str(tag_count)+') > span >a::text').extract())
		cover = response.css('body > div.container > div.row.movie > div.col-md-9.screencap > a > img::attr(src)').extract_first()

		#提取ajax 磁力链接
		gid = re.search(r'var gid = (.*);',response.body)
		img = re.search(r'var img = \'(.*)\';',response.body)

		# magnet_url = "\r\n".join(self.ajax_magnet(gid.group(1),img.group(1)))
		magnet_url = self.ajax_magnet(gid.group(1),img.group(1))
		# #提取ajax过后的磁力链接
		# driver = webdriver.PhantomJS()
		# driver.get(response.request.url)
		# content = driver.page_source.encode('utf-8')
		# driver.quit()
		# response = response.replace(body = content)
		# magnet_url = response.xpath('//*[@id="magnet-table"]/tr[1]/td[2]/a/@href').extract_first().replace(' ','').replace('\t','').replace('\n','')
		# size = response.xpath('//*[@id="magnet-table"]/tr[1]/td[2]/a/text()').extract_first().replace(' ','').replace('\t','').replace('\n','')
		
				
		yield {
				"code":code,
				"title":title,
				"actor":actor,
				'publish_date':publish_date,
				'tag':tag,
				'cover':cover,
				'size_and_magnet_link':magnet_url,
		}



	def ajax_magnet(self,gid,img):
		import gzip
		import StringIO
		from bs4 import BeautifulSoup
		import urllib2
		import random
#https://i.pximg.net/img-original/img/2017/02/11/00/09/24/61384715_p0.jpg
		magnet_header = {
			"accept":"*/*",
			"accept-encoding":"gzip, deflate, br",
			"accept-language":"zh-CN,zh;q=0.8",
			# "cookie":"__cfduid=dc184bb69ff233b63211e3d141ca009e11500690375; PHPSESSID=qaknp50olrqndu392drcefrs56; HstCfa2807330=1500690371254; HstCmu2807330=1500690371254; HstCla2807330=1500690574848; HstPn2807330=5; HstPt2807330=5; HstCnv2807330=1; HstCns2807330=1; __dtsu=2DE7B66BD0B772592143ACB002F15214",
			"referer":"https://www.javbus.com",
			"user-agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
			"x-requested-with":"XMLHttpRequest",
		}
		floor = str(random.randint(1, 1000))
		# img = quote(img)
		url = "https://www.javbus.com/ajax/uncledatoolsbyajax.php?gid="+gid+"&lang=zh&img="+img+"&uc=0&floor="+floor
		#url = "https://www.baidu.com"
		
		# f = open("1.html",'wb') #创建文件对象准备写入，还可以更精简
		src_req = urllib2.Request(url,headers = magnet_header) #创建request对象
		html = urllib2.urlopen(src_req).read()
		data = StringIO.StringIO(html)
		gzipper = gzip.GzipFile(fileobj=data)
		html = gzipper.read()
		soup = BeautifulSoup(html,"lxml")
		magnet_list = []
		for tr in soup.find_all('tr'):
			i = 0
			for td in tr.find_all('td'):
				if i is 1:
					magnet_list.append(td.get_text().strip()+"|"+td.a['href'])
				i = i+1
		return magnet_list
		
		# f.write(html) #用Request对象返回数据作为对象写入文件
		# f.close()
