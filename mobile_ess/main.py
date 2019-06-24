from scrapy.cmdline import execute
import  logging,sys,re

execute(["scrapy", "crawl", "ess", "-a", "broadbandNo=010151" , "-a", "startNo=00000", "-a", "endNo=100000"])
