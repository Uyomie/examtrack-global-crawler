import scrapy
from scrapy import signals
from pydispatch import dispatcher
from scrapy.utils.project import get_project_settings
from ..items import UnivJournalItem

class UnivJournalSpider(scrapy.Spider):
    name = 'univ-journal'
    allowed_domains = ['univ-journal.jp']
    start_urls = [f'https://univ-journal.jp/daigakuin-list/?_page={page}' for page in range(1, 24)]
    processed_info = [] 

    def __init__(self, *args, **kwargs):
        super(UnivJournalSpider, self).__init__(*args, **kwargs)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        settings = get_project_settings()
        self.download_delay = settings.get('DOWNLOAD_DELAY')
        self.concurrency = settings.get('CONCURRENT_REQUESTS')

    def parse(self, response):
        page_number = response.url.split('_page=')[-1]  # Current page
        cards = response.xpath('//div[contains(@class, "pt-cv-content-item")]')
        for index, card in enumerate(cards, start=1):
            grad_school_name = card.xpath('.//h4/a/text()').get()
            majors = card.xpath('.//div[contains(@class, "pt-cv-custom-fields")]/div[@class="pt-cv-ctf-value"]/text()').getall()
            detail_url = card.xpath('.//div[contains(@class, "pt-cv-rmwrap")]/a/@href').get()
            if detail_url is not None:
                for major in majors:
                    yield response.follow(detail_url, self.parse_detail, cb_kwargs={'grad_school_name': grad_school_name, 'major': major}, dont_filter=True)
            self.processed_info.append(f'Page {page_number} Card {index}: {grad_school_name}')

    def parse_detail(self, response, grad_school_name, major):
        grad_school_url = response.xpath('//td[contains(text(), "公式ページ")]/following-sibling::td/text()').get()
        item = UnivJournalItem(
            grad_school_name=grad_school_name,
            major=major,
            grad_school_url=grad_school_url if grad_school_url else None
        )
        yield item

    def spider_closed(self, spider):
        # log all processed records
        spider.logger.info("Processed Pages and Cards:")
        for info in self.processed_info:
            spider.logger.info(info)
