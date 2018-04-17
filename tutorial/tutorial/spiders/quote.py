# -*- coding: utf-8 -*-
import scrapy
from ..items import QuoteItem

class QuoteSpider(scrapy.Spider):
    name = 'quote'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']

    # 默认的callback函数
    def parse(self, response):
        for quote in response.xpath('//div[@class="quote"]'):
            text = quote.xpath('//span[@class="text"]/text()').extract_first()
            tags = quote.css('div.tags a.tag::text').extract()
            author_info = quote.css('a[href*="/author"]::attr(href)').extract_first()
            author_info_url = response.urljoin(author_info)
            # 发送获取author_info的请求
            yield scrapy.Request(author_info_url, callback=self.parse_author_info,
                                 meta={'text': text,
                                       'tags': tags,
                                       })
            # 下一页
            next_page = response.xpath('//li[@class="next"]/a/@href').extract_first()
            next_page_url = response.urljoin(next_page)
            yield response.follow(next_page_url)

    # 处理author_info的函数
    def parse_author_info(self, response):
        text = response.meta['text']
        tags = response.meta['tags']
        author_name = response.xpath('//h3/text()').extract_first().strip().strip('\n')
        author_born_date = response.xpath('//span[@class="author-born-date"]/text()').extract_first()
        author_born_location = response.xpath('//span[@class="author-born-location"]/text()').extract_first()
        author_desc = response.xpath('//div[@class="author-description"]/text()').extract_first().strip('\n').strip()
        author = {
            'author_name': author_name,
            'author_born_date': author_born_date,
            'author_born_location': author_born_location,
            'author_desc': author_desc,
        }
        item = QuoteItem()
        for field in item.fields:
            try:
                item[field] = eval(field)
            except:
                print('Field is not defined', field)
        yield item
