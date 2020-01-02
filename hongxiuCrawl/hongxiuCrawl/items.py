# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HongxiucrawlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class HongxiuBookListItem(scrapy.Item):
    # 小说ID
    novelId = scrapy.Field()
    # 小说名称
    novelName = scrapy.Field()
    # 小说链接
    novelLink = scrapy.Field()
    # 小说作者
    novelAuthor = scrapy.Field()
    # 小说类型
    novelType = scrapy.Field()
    # 小说状态
    novelStatus = scrapy.Field()
    # # 小说更新时间
    # novelUpdateTime = scrapy.Field()
    # 小说字数
    novelWorlds = scrapy.Field()
    # 小说章节数
    novelSections = scrapy.Field()
    # 小说简介
    novelIntro = scrapy.Field()
    # 小说封面
    novelImageUrl = scrapy.Field()

class HongxiuBookDetailItem(scrapy.Item):
    # 小说Id
    novelId = scrapy.Field()
    # 小说总点击量
    novelAllClick = scrapy.Field()
    # 小说总收藏
    novelAllCollect = scrapy.Field()
    # 小说创作天数
    novelDays = scrapy.Field()
    # 小说本周票数
    novelWeekPoll = scrapy.Field()
    # 小说本月票数
    novelMonthPoll = scrapy.Field()


