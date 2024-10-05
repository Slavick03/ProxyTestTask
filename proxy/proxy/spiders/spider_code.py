import time
import scrapy
import base64
from scrapy.crawler import CrawlerProcess


class ProxySpider(scrapy.Spider):
    name = 'proxy'
    allowed_domains = ['free-proxy.cz']
    start_urls = ['http://free-proxy.cz/en/']

    def parse(self, response):
        self.logger.info(f"Processing {response.url}")

        rows = response.xpath('//table[@id="proxy_list"]/tbody/tr')
        self.logger.info(f"Found {len(rows)} rows")

        for index, row in enumerate(rows):
            encoded_ip = row.xpath('.//td[1]/script/text()').re_first(r'document\.write\(Base64\.decode\("([^"]+)"\)\)')
            if encoded_ip:
                try:
                    ip_address = base64.b64decode(encoded_ip).decode('utf-8')
                except Exception as e:
                    self.logger.error(f"Error decoding IP: {e}")
                    ip_address = None
            else:
                ip_address = None

            port = row.xpath('.//td[2]//text()').get()

            # Печать информации на экран и генерация данных для экспорта
            if ip_address and port:
                scraped_info = {
                    'ip_address': ip_address,
                    'port': port,
                }
                yield scraped_info
            else:
                self.logger.warning(f"Missing IP or port at row {index}")

        # Переход на следующую страницу, если она существует
        next_page = response.xpath('//a[text()="Next »"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)


def format_time(seconds):
    return time.strftime("%H:%M:%S", time.gmtime(seconds))


# Создание и настройка процесса Scrapy
process = CrawlerProcess(settings={
    'LOG_LEVEL': 'INFO',  # Устанавливаем уровень логов (DEBUG, INFO, WARNING)
    'FEEDS': {
        'proxies.csv': {
            'format': 'csv',
            'encoding': 'utf8',
            'fields': ['ip_address', 'port'],
        },
    },
})

start_time = time.time()

# Старт паука
process.crawl(ProxySpider)
process.start()  # Этот метод автоматически запускает и завершает reactor

end_time = time.time()
elapsed_time = end_time - start_time
formatted_time = format_time(elapsed_time)

# Сохранение времени выполнения в файл
with open('time.txt', 'w') as time_file:
    time_file.write(f"Time taken: {formatted_time}\n")

print(f"Time taken: {formatted_time}\n")
