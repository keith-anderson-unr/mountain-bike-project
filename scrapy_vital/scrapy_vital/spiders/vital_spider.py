import scrapy
import requests
import csv
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from bs4 import BeautifulSoup
import os
import pandas as pd



class ScraperItem(scrapy.Item):
    # The source URL
    url_from = scrapy.Field()
    # The destination URL
    url_to = scrapy.Field()

class VitalSpider(CrawlSpider):
    name = "vitalbikechecks"
    allowed_domains = ["www.vitalmtb.com"]
    start_urls = ['https://www.vitalmtb.com/community/main?cat=Bike+Check&page=1&scope=newest']

    rules = [
        Rule(
            LinkExtractor(allow='setup,', deny = 'mobile=true'),
            follow=True,
            callback="parse_bike"
        )
    ]

    def parse_bike(self, response):
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
        path = '/home/ec2-user/data/raw_files'
        export_path = os.path.join(path, file_name + '_setup.csv')
        df.to_csv (path_or_buf = export_path, index = False, header=True)