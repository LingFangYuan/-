# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from os.path import join

import scrapy
from scrapy.pipelines.images import ImagesPipeline


class DeskzolspiderPipeline(object):
    def process_item(self, item, spider):
        return item


class MyImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        index = 0
        for image_url in item['image_urls']:
            index += 1
            yield scrapy.Request(image_url, meta={'item': item, 'index': index})

    def file_path(self, request, response=None, info=None):
        item = request.meta['item']
        index = request.meta['index']
        title = item['title']
        suffix = request.url.split('/')[-1].split('.')[-1]
        image_name = str(index) + '.' + suffix
        file_name = join('full', title, image_name).replace('\\', '/')

        return file_name
