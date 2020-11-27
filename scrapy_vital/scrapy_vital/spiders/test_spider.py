import scrapy
import requests
import csv
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from bs4 import BeautifulSoup
import pandas as pd
from IPython.display import display_html
import os



class QuotesSpider(scrapy.Spider):
    name = 'testID'
    start_urls = [
        'https://www.vitalmtb.com/community/jakub-r,53780/setup,42906?cat=Bike+Check&page=1&riding_types%5B%5D=4&scope=newest'
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        # Find unique bike_id and convert to string
        bike_id = response.css('div.b-bike-checks-item::attr(setup-check-id)').extract()
        bike_id = str(bike_id[0])
        # Parse html response into text
        html_content = requests.get(response.url).text
        soup = BeautifulSoup(html_content, 'lxml')
        # Retrieve table element with bike data
        bike_table = soup.find('table', attrs={'class': 'setup-checks-specs'})
        # Convert html table into dataframe
        df = pd.read_html(str(bike_table))[0]
        df = pd.DataFrame(df, columns = ['Parts', 'Brand', 'Model'])
        # add additional_data to dataframe - setup data points
        desc_table = response.xpath('//*[@class ="setup-check-specs"]//tbody')
        rows = desc_table.xpath('//tr')
        model_year = rows[-3]
        model_year_text = model_year.xpath('td//text()')[0].extract()
        riding_type = rows[-2]
        riding_type_text = riding_type.xpath('td//text()')[0].extract()
        user_id = response.xpath('//span[@class ="id"]/text()')[0].extract()
        user_name = response.xpath('//span[@class ="nickname"]/text()')[0].extract()
        # add data points to dataframe
        df['id'] = bike_id
        df['model_year'] = model_year_text
        df['riding_type'] = riding_type_text
        df['user_id'] = user_id
        df['user_name'] = user_name
        # write to csv
        file_name = bike_id
        path = '/Users/keithanderson/Desktop/Testing/Final'
        export_path = os.path.join(path, file_name + '.csv')
        df.to_csv (path_or_buf = export_path, index = False, header=True)