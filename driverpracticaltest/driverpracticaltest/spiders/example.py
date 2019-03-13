# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import FormRequest
import json

import os


DRIVER_LICENCE_NUMBER = ""
PREFERED_DATE = "23/03/19"

class ExampleSpider(scrapy.Spider):
    name = 'example'
    def start_requests(self):
        urls = [
            'https://www.gov.uk/book-driving-test',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        start_now_href = response.css('.gem-c-button::attr(href)').get()
        self.log('Follow the address %s' % start_now_href)
        yield response.follow(start_now_href, callback=self.parse_type)

    def parse_type(self, response):
        yield FormRequest.from_response(response,
                                        formdata={"testTypeCar": "Car (manual and automatic)"},
                                        callback=self.parse_licence
        )

    def parse_licence(self, response):
        yield FormRequest.from_response(response,
                                        formdata={
                                            "driverLicenceNumber": DRIVER_LICENCE_NUMBER,
                                            "extendedTest": "false",
                                            "specialNeeds": "false"
                                        },
                                        callback=self.parse_date
        )

    def parse_date(self, response):
        yield FormRequest.from_response(response,
                                        formdata={
                                            "preferredTestDate": PREFERED_DATE
                                        },
                                        callback=self.parse_center_search
        )


    def parse_center_search(self, response):
        yield FormRequest.from_response(response,
                                        formdata={
                                            "testCentreName": "SM44PE"
                                        },
                                        callback=self.parse_center
        )


    def parse_center(self, response):
        morden_url = response.css('#centre-name-128::attr(href)').get()
        yield response.follow(morden_url, callback=self.parse_calendar)

    def parse_calendar(self, response):
        result = []
        for slot in response.css('input.SlotPicker-slot'):
            date_str = slot.attrib['data-datetime-label']
            self.log('Slot available: %s' % date_str)
            result.append(date_str)

        self.update_json(result)

    def update_json(self, items):
        # mstr='Done! 100 slots have been found'
        # os.system('notify-send ' + mstr)
        with open('data.json', 'w') as outfile:
            json.dump(items, outfile, indent=4)