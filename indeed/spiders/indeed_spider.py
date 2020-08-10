import re
import scrapy
from bs4 import BeautifulSoup


class IndeedSpider(scrapy.Spider):
    name = "indeed_spider"
    allowed_domains = ["indeed.com"]
    # currently using full time job scrapping.
    start_urls = ["https://www.indeed.com/jobs?q=full%20time&l=New%20York"]
    base_url = "http://www.indeed.com"
    # FULL_TIME = "full%20time&l=New%20York"
    # PART_TIME = "part%20time&l=New%20York"
    # CONTRACT = "contract&l=New%20York"
    # INTERNSHIP = "internship&l=New%20York"
    # TEMPORARY = "temporary&l=New%20York"
    # COMMISSION = "commission&l=New%20York"

    def parse_job(self, response):
        print("Inside parse_job-----------------------------------------------")

        # using bs4 because job description has nested tags and it makes code messy to extract text from these tags.
        soup_obj = BeautifulSoup(response.text, features='html5lib')
        text = soup_obj.find("div",
                             attrs={"id": "jobDescriptionText", "class": "jobsearch-jobDescriptionText"}).get_text()
        lines = (line.strip() for line in text.splitlines())
        text = " ".join(line for line in lines if line)

        yield {"FULL_TIME": text}

    def parse_jobs(self, response):
        print("Inside parse_jobs-----------------------------------------------")
        job_link_area = response.xpath('//*[@id="resultsCol"]')
        job_urls = job_link_area.xpath('.//a/@href').extract()
        job_link_area = list(filter(lambda x: 'clk' in x, job_urls))
        job_urls = [self.base_url + link for link in job_link_area]

        for j in range(0, len(job_urls)):
            request = scrapy.Request(url=job_urls[j], callback=self.parse_job)
            yield request

    def parse(self, response):
        num_jobs_area = response.xpath('//*[@id="searchCountPages"]/text()').get()
        job_numbers = re.findall(r'\d+', num_jobs_area)

        if len(job_numbers) >= 3:
            total_num_jobs = (int(job_numbers[1]) * 1000) + int(job_numbers[2])
        else:
            total_num_jobs = int(job_numbers[1])

        # Total jobs
        print("There were", total_num_jobs, "jobs found,")
        num_pages = int(total_num_jobs / 10)
        # you can limit the num_pages to your desired value.

        for i in range(1, num_pages+1):
            print("Getting page", i)
            start_num = str(i * 10)
            current_page = "".join([self.start_urls[0], "&start=", start_num])
            request = scrapy.Request(url=current_page, callback=self.parse_jobs)
            yield request
