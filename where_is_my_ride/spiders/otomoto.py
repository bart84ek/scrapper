import scrapy


class OtomotoSpider(scrapy.Spider):
    name = 'otomoto'
    url = 'https://www.otomoto.pl/osobowe/BRAND/MODEL/?search%5Border%5D=created_at%3Adesc&search%5Bbrand_program_id%5D%5B0%5D=&search%5Bcountry%5D='

    custom_settings = {
       'USER_AGENT': "Mozilla/5.0 (X11; Linux x86_64) "
    }

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
        offers = response.css('article.offer-item')
        for offer in offers:
            title = offer.css('a.offer-title__link::text').get()
            price = offer.css('.offer-price__number span::text').get()
            yield {
                'title': title.strip(),
                'price': price.strip()
            }

        next_page = response.css('ul.om-pager li.next a::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
