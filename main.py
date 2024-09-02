import requests
import time
from lxml import etree
import sqlite3

conn = sqlite3.connect("jobs.db")
cursor = conn.cursor()
max_page = 100

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY,
    company_name TEXT,
    job_position TEXT,
    workplace TEXT,
    job_content TEXT,
    work_experience TEXT,
    educational TEXT,
    industry TEXT,
    apply_unmber TEXT,
    salary TEXT,
    number_employees TEXT,
    job_update_time TEXT
)
"""
)


area = "6001006002%2C6001006001"
jobcat = "2007001000"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
}


def get_104_response(page_number):
    response = requests.get(
        "https://www.104.com.tw/jobs/search/?ro=0&jobcat="
        + jobcat
        + "&expansionType=area%2Cspec%2Ccom%2Cjob%2Cwf%2Cwktm&area="
        + area
        + "&order=17&asc=0&zone=16&page="
        + str(page_number)
        + "&mode=s&jobsource=index_s&langFlag=0&langStatus=0&recommendJob=1&hotJob=1",
        headers=headers,
        verify=None,
    )

    return response


if __name__ == "__main__":

    for i in range(1, max_page + 1):

        response = get_104_response(i)
        html = etree.HTML(response.content)

        empty_page_element = html.xpath('//*[@id="js-job-content"]/div/div[2]/p[1]')

        if len(empty_page_element) > 0:
            empty_page = empty_page_element[0].text.strip()

            if "搜尋結果好像很少" in empty_page:
                print(empty_page)
                break

        for article in html.xpath('//*[@id="js-job-content"]/article'):
            company_name = None
            job_position = None
            workplace = None
            job_content = None
            work_experience = None
            educational = None
            industry = None
            apply_unmber = None
            number_employees = None
            salary = None

            # //*[@id="js-job-content"]/article[4]/div[1]/ul[1]/li[2]/a
            company_name_element = article.xpath("./div[1]/ul[1]/li[2]/a")
            if len(company_name_element) > 0:
                company_name = company_name_element[0].text.strip()
                print(company_name)

            # //*[@id="js-job-content"]/article[4]/div[1]/h2/a
            job_position_element = article.xpath("./div[1]/h2/a")
            if len(job_position_element) > 0:
                job_position = job_position_element[0].text.strip()
                print(job_position)

            # //*[@id="js-job-content"]/article[4]/div[1]/ul[2]/li[1]
            workplace_element = article.xpath("./div[1]/ul[2]/li[1]")
            if len(workplace_element) > 0:
                workplace = workplace_element[0].text.strip()
                print(workplace)

            # //*[@id="js-job-content"]/article[4]/div[1]/p
            job_content_element = article.xpath("./div[1]/p")
            if len(job_content_element) > 0:
                job_content = job_content_element[0].text.strip()
                print(job_content)

            # //*[@id="js-job-content"]/article[7]/div[1]/div
            job_tags_element = article.xpath("./div[1]/div/a")
            for tag in job_tags_element:

                if "員工" in tag.text.strip():
                    number_employees = tag.text.strip()
                    print(tag.text.strip())
                if "月薪" in tag.text.strip():
                    salary = tag.text.strip()
                    print(tag.text.strip())

            # //*[@id="js-job-content"]/article[24]/div[1]/ul[2]/li[2]
            work_experience_element = article.xpath("./div[1]/ul[2]/li[2]")
            if len(work_experience_element) > 0:
                work_experience = work_experience_element[0].text.strip()
                print(work_experience)

            # //*[@id="js-job-content"]/article[24]/div[1]/ul[2]/li[3]
            educational_element = article.xpath("./div[1]/ul[2]/li[3]")
            if len(educational_element) > 0:
                educational = educational_element[0].text.strip()
                print(educational)

            # //*[@id="js-job-content"]/article[4]/div[1]/ul[1]/li[3]
            industry_element = article.xpath("./div[1]/ul[1]/li[3]")
            if len(industry_element) > 0:
                industry = industry_element[0].text.strip()
                print(industry)

            # //*[@id="js-job-content"]/article[8]/div[2]/a
            apply_unmber_element = article.xpath("./div[2]/a")
            if len(apply_unmber_element) > 0:
                apply_unmber = apply_unmber_element[0].text.strip()
                print(apply_unmber)

            # //*[@id="js-job-content"]/article[14]/div[1]/h2/span
            job_update_time_element = article.xpath("./div[1]/h2/span")
            if len(job_update_time_element) > 0:
                job_update_time = job_update_time_element[0].text.strip()
                print(job_update_time)

            cursor.execute(
                "SELECT company_name, job_position FROM jobs WHERE company_name = ? AND job_position = ?",
                (company_name, job_position),
            )

            result = cursor.fetchone()

            if not result:
                cursor.execute(
                    """
                        INSERT INTO jobs (company_name,
                            job_position,
                            workplace,
                            job_content,
                            work_experience,
                            educational,
                            industry,
                            apply_unmber,
                            number_employees,
                            salary,
                            job_update_time)
                        VALUES
                            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        company_name,
                        job_position,
                        workplace,
                        job_content,
                        work_experience,
                        educational,
                        industry,
                        apply_unmber,
                        number_employees,
                        salary,
                        job_update_time,
                    ),
                )

            conn.commit()

            print("-------------------------------")

        time.sleep(1)
