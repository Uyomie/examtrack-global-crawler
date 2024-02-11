import scrapy
from examtrack_global_crawler.items import DaigakuinItem

class DaigakuinSpider(scrapy.Spider):
    name = 'daigakuin'
    allowed_domains = ['www.daigakuin.ne.jp']
    start_urls = ['https://www.daigakuin.ne.jp/apl/retrieval/retrieval.do']
    
    def start_requests(self):
        # Initial form data
        formdata = {
            'searchCond_keyword': '',
            'studyType': '99',
            'searchCond_state': '99'
        }
        yield scrapy.FormRequest(
            url="https://www.daigakuin.ne.jp/apl/retrieval/resultList.do",
            formdata=formdata,
            callback=self.parse
        )
    def construct_full_url(self, js_call):
        # Extract the path from a JavaScript function call
        path = js_call.split("'")[1]  # Extract the contents in single quotes
        # Construct the full URL
        return f"https://www.daigakuin.ne.jp{path}"

    def parse(self, response):
        #Extract grad school, major, and URL of the grad school.
        for row in response.css('#searchFunc-resultTable > tbody > tr'):
            item = DaigakuinItem()
            grad_school_name = row.css('em.schoolName::text').get()
            major = row.css('span.speciality::text').get()
            js_call = row.css('td.introduction > a::attr(href)').get()

            # Check for JavaScript calls
            if js_call and js_call.startswith('javascript'):
                grad_school_url = self.construct_full_url(js_call)
            else:
                # If it's not a JavaScript call, use the data directly
                grad_school_url = response.urljoin(js_call) if js_call else None
            
            item['grad_school_name'] = grad_school_name.strip() if grad_school_name else None
            item['major'] = major.strip() if major else None
            item['grad_school_url'] = grad_school_url

            yield item
        
        # Calculating form data for the next page
        current_page = response.css('input[name="pageID"]::attr(value)').get()
        if current_page:
            current_page = int(current_page)
            next_page = current_page + 1
            start = next_page * 30 - 29

            formdata = {
                'start': str(start),
                'recordBeginNo': str(start),
                'recordEndNo': str(start + 29),
                'resultCnt': '1949',
                'startId': str(start),
                'pageID': str(next_page),
                'searchCond_keyword': '',
                'studyType': '99',
                'searchCond_classification': '',
                'searchCond_type': '',
                'searchCond_state': '99',
                'searchCond_howtostudy_1': '',
                'searchCond_howtostudy_2': '',
                'searchCond_howtostudy_3': '',
                'searchCond_howtostudy_4': '',
                'searchCond_howtostudy_5': '',
                'searchCond_howtostudy_6': '',
                'sortDivisionUpFlag': 'Off',
                'sortDivisionUpFlagGif': 'off',
                'sortDivisionDownFlag': 'Off',
                'sortDivisionDownFlagGif': 'off',
                'sortBaseAdUpFlag': 'Off',
                'sortBaseAdUpFlagGif': 'off',
                'sortBaseAdDownFlag': 'Off',
                'sortBaseAdDownFlagGif': 'off'
            }
            yield scrapy.FormRequest(
                url="https://www.daigakuin.ne.jp/apl/retrieval/resultList.do",
                formdata=formdata,
                callback=self.parse
            )
        else:
            print(f'Error: Unable to extract current_page. Check the selector or page structure.')