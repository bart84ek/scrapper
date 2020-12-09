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
            css = '''a.detailsLink::attr(href),
            a.detailsLinkPromoted::attr(href)'''
            url = auction.css(css).get()
            if url.find('www.olx.pl') > 0:
                yield response.follow(url, callback=self.parse_details)
            else:
                yield response.follow(url, callback=self.parse_otomoto_details)

        next_page = response.css('.pager span.next a::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_details(self, response):
        id_css = 'div.offer-titlebox__details > * > small::text'
        title_css = '.offer-titlebox h1::text'
        user = '.offer-user__details a::text'
        user_url_css = '.offer-user__details a::attr(href)'
        price_css = '.price-label strong::text'
        image_css = '.gallery_img.img-item img::attr(src)'
        category_css = '#breadcrumbTop ul > li a::attr(title)'
        localization_css = '.offer-titlebox__details a *::text'
        added_css = '.offer-titlebox__details > em::text'
        params_css = '.descriptioncontent table.details tr td *::text,' \
            '.descriptioncontent table.details tr th::text'
        desc_css = '#textContent *::text'
        views_css = '#offerbottombar .pdingtop10 strong::text'
        data = {
            'url': response.url,
            'id': response.css(id_css).get(),
            'title': response.css(title_css).get().strip(),
            'user': response.css(user).get().strip(),
            'userUrl': response.css(user_url_css).get(),
            'price': response.css(price_css).get(),
            'image': response.css(image_css).get(),
            'category': response.css(category_css).getall(),
            'localization': response.css(localization_css).get(),
            'added': response.css(added_css).get().strip(),
            'params': self.trim_params(response.css(params_css).getall()),
            'description': response.css(desc_css).get().strip(),
            'views': response.css(views_css).get(),
        }
        yield data

    def parse_otomoto_details(self, response):
        offer = response.css('.offer-summary')
        title_css = 'span.offer-title::text'
        price = offer.css('.offer-price::attr(data-price)')
        meta_css = response.css('.offer-meta .offer-meta__value::text')
        image = response.css('img.bigImage::attr(data-lazy)')
        category = response.css('ul.breadcrumb li.breadcrumb__item a span::text')
        params_css = '.offer-params__item .offer-params__label::text,' \
            '.offer-params__item .offer-params__value::text,' \
            '.offer-params__item .offer-params__value a::text'

        desc_css = '.offer-description__description::text'
        user_link = '.seller-box__seller-name a'
        user_name = '.seller-box__seller-name::text'
        link = response.css(user_link)
        if link.get() is None:
            user = response.css(user_name).get()
            user_url = None
        else:
            user = response.css(user_link+"::text").get()
            user_url = response.css(user_link+"::attr(href)").get()

        meta = meta_css.getall()
        data = {
            'url': response.url,
            'id': meta[1],
            'title': (" ").join(offer.css(title_css).getall()).strip(),
            'user':  user.strip(),
            'userUrl': user_url,
            'price': price.get(),
            'added': meta[0],
            'image': image.get(),
            'category': category.getall(),
            'params': self.trim_params(response.css(params_css).getall()),
            'description': response.css(desc_css).getall(),
            'views': None
        }
        yield data

    def trim_params(self, params):
        out = []
        for param in params:
            stripped = param.strip()
            if stripped != '':
                out.append(stripped)
        return out
