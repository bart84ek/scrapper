import scrapy


class OlxSpider(scrapy.Spider):
    name = 'olx'
    url = 'https://www.olx.pl/motoryzacja/samochody/q-SEARCH/'

    custom_settings = {
       'USER_AGENT': "Mozilla/5.0 (X11; Linux x86_64) "
    }

    def start_requests(self):
        search = getattr(self, 'search', None)

        if search is not None:
            url = self.url.replace('SEARCH', search)
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        print(response.css('body').get())
        for auction in response.css('tr.wrap'):
            print("AAAA")
            yield {
                'auction': auction.getall()
                }
