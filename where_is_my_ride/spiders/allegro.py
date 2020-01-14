# -*- coding: utf-8 -*-
import scrapy
import re


class AllegroSpider(scrapy.Spider):
    name = 'allegro'
    url = 'https://allegro.pl/kategoria/samochody-osobowe-4029?string=BRAND%20MODEL'

    def start_requests(self):
        brand = getattr(self, 'brand', None)
        model = getattr(self, 'model', None)
        url = self.url

        if brand is not None:
            url = url.replace('BRAND', brand)

        if model is not None:
            url = url.replace('MODEL', model)

        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        for auction in response.css('article[data-item="true"]'):
            url = auction.css('h2').css('a::attr(href)').get()
            yield response.follow(url, callback=self.parse_details)

        next_page = response.css('a[data-role="next-page"]::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_details(self, response):
        yield {
            'title': response.css('h1::text').get(),
            'user': response.css('a[data-analytics-click-value="sellerLogin"]::text').get(),
            'price': response.css('div[aria-label*="cena"]::attr(aria-label)').get(),
            'till': response.css('time::attr(datetime)').get(),
            'image': response.css('meta[itemprop="image"]::attr(content)').get(),
            'category': response.css('div[data-role="breadcrumb-item"] span[itemprop="name"]::text').getall(),
            'parameters': response.css('a[name="parameters"] + div').css('li *::text').getall(),
            'description': "\n".join(response.css('a[name="container-description"] + div').css('*::text').getall())
        }

    def remove_html_tags(self, data):
        p = re.compile(r'<.*?>')
        return p.sub('', data)
