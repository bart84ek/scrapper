import scrapy


class OlxSpider(scrapy.Spider):
    name = 'olx'
    url = 'https://www.olx.pl/motoryzacja/samochody/q-BRAND-MODEL/'

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
        for auction in response.css('tr.wrap'):
            url = auction.css('a.detailsLink::attr(href), a.detailsLinkPromoted::attr(href)').get()
            print(url)
            if url.find('www.olx.pl') > 0:
                yield response.follow(url, callback=self.parse_details)
            else:
                yield response.follow(url, callback=self.parse_otomoto_details)

    def parse_details(self, response):
        print("OLX!")
        yield {
            'title': response.css('.offer-titlebox h1::text').get().strip(),
            # 'user': response.css('a[data-analytics-click-value="sellerLogin"]::text').get(),
            'price': response.css('.price-label strong::text').get(),
            # 'till': response.css('time::attr(datetime)').get(),
            # 'image': response.css('meta[itemprop="image"]::attr(content)').get(),
            # 'category': response.css('div[data-role="breadcrumb-item"] span[itemprop="name"]::text').getall(),
            # 'parameters': response.css('a[name="parameters"] + div').css('li *::text').getall(),
            # 'description': "\n".join(response.css('a[name="container-description"] + div').css('*::text').getall())
        }

    def parse_otomoto_details(self, response):
        print("otomoto!")
        yield {
            'title': 'todo',
        }
