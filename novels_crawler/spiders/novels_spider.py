from parsel import selector
from novels_crawler.novel_chapter import NovelChapter
from novels_crawler import session
from sqlalchemy.sql.sqltypes import String
from novels_crawler.novels import Novel
import scrapy
import re

from scrapy.selector.unified import Selector


class NovelsSpider(scrapy.Spider):
    name = "novels"
    allow_domains = [""]

    start_urls = [
        "http://m.txtwan.cc/sort/"
    ]

    def parse(self, response):
        sel = Selector(text=response.text, type='html')
        category = sel.xpath('//section[@class="sorttop"]/ul/li/a/@href')

        for c in category.extract():
            url = "http://m.txtwan.cc{}".format(c)
            yield scrapy.Request(url, callback=self.parse_category)

    def parse_category(self, response):
        sel = Selector(text=response.text, type='html')
        novel = sel.xpath('//ul[@class="xbk"]/li/a/@href')

        for n in novel.extract():
            url = "http://m.txtwan.cc/read/{}/".format(str(n).split(".")[0].split("/")[2])
            yield scrapy.Request(url, callback=self.parse_novel)

        
        show_page = sel.xpath('//div[@class="page"]/a')
        next_page = -1
        end_page = -1
        next_href = show_page
        for a in show_page:
            s = str(a.extract())
            href = str(a.xpath('./@href').extract_first())
            page = -1
            if href != None:
                page = int(href.split("/")[2].split('_')[1])
            if s.find('下一页') > 0:
                next_page = page
                next_href = a
            elif s.find('尾页') > 0:
                end_page = page

        if next_page <= end_page and next_page >= 0 and end_page >= 0:
            href = next_href.xpath('./@href').extract_first()
            url = "http://m.txtwan.cc{}".format(href)
            yield scrapy.Request(url, callback=self.parse_category)    


    def parse_novel(self, response):
        sel = Selector(text=response.text, type='html')
        chapter = sel.xpath(
            '//html/body/section[@id="zjlb_b2xiaoshuo"]/ul[@class="lb fk_b2xiaoshuo"]/li/a/@href')

        for chapter in chapter.extract():
            url = "http://m.txtwan.cc{}".format(chapter)
            chapter = str(chapter).split(".")[0].split("/")
            novel_chapter = session.query(NovelChapter).filter(NovelChapter.novel_chapter_index == chapter[3]).first()
            if novel_chapter == None:
                yield scrapy.Request(url, callback=self.parse_chapter)

        showPage = sel.xpath('//div[@class="page"]/a')
        nextPage = -1
        endPage = -1
        next_href = showPage
        for a in showPage:
            s = str(a.extract())
            href = a.xpath('./@href').extract_first()
            page = -1
            if href != None:
                page = int(href.split('/')[2].split('_')[1])
            if s.find("下一页") > 0:
                nextPage = page
                next_href = a
            elif s.find("尾页") > 0:
                endPage = page

        if nextPage <= endPage and nextPage >= 0 and endPage >= 0:
            href = next_href.xpath('./@href').extract_first()
            url = "http://m.txtwan.cc{}".format(href)
            yield scrapy.Request(url, callback=self.parse_novel)
                

    def parse_chapter(self, response):
        sel = Selector(text=response.text, type='html')
        title = sel.xpath('//html/body/header/div[@class="zhong"]/h2/text()')
        author = sel.xpath(
            '//html/body/section[@class="zj"]/p[@id="con_info_b2xiaoshuo"]/a/text()')
        novel_id = re.search('/read/[0-9]*', response.text).group()[6:]
        novel_chapter_index = re.search('编号:[0-9]*', response.text).group()[3:]
        novel_chapter_title = sel.xpath(
            '//html/body/section[@class="zj"]/div[@class="con_title_b2xiaoshuo"]/h1[@id="con_title_b2xiaoshuo"]/text()')
        chapter = sel.xpath('//html/body/section[@class="zj"]/article/text()')

        content = ""

        for c in chapter.extract():
            p = str(c).strip()
            content += p + "\n"

        novel = session.query(Novel).filter(Novel.novel_id == novel_id).first()

        if novel == None:
            novel = Novel()
            novel.title = title.extract_first()
            novel.author = author.extract_first()
            novel.novel_id = novel_id
            novel_chapter = NovelChapter()
            novel_chapter.content = content
            novel_chapter.novel_chapter_index = novel_chapter_index
            novel_chapter.novel_id = novel_id
            novel_chapter.title = novel_chapter_title.extract_first()
            session.add(novel)
            session.commit()
            session.add(novel_chapter)
            session.commit()
        else:
            novel_chapter = NovelChapter()
            novel_chapter.content = content
            novel_chapter.novel_chapter_index = novel_chapter_index
            novel_chapter.title = novel_chapter_title.extract_first()
            novel_chapter.novel_id = novel_id
            session.add(novel_chapter)
            session.commit()
