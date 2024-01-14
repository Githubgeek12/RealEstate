import asyncio
from RE_detail import detail
import csv
import re
import time
from pyppeteer import launch
from bs4 import BeautifulSoup
from pyppeteer_stealth import stealth
import functools

path = '/Users/trishika/PycharmProjects/pythonProject'
place = 'ny'
f_path = '/Users/trishika/PycharmProjects/pythonProject/data/output_' + place + '.csv'


def retry(max_retries, delay=1):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for _ in range(max_retries):
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    print(f"Retrying after error: {e}")
                    time.sleep(delay)
            raise Exception(f"Max retries reached for {func.__name__}")

        return wrapper

    return decorator


async def main():
    await scrape_data()


@retry(max_retries=3)
async def scrape_data():
    try:
        browser = await launch({'headless': False})
        page = await browser.newPage()
    except Exception:
        raise Exception('Error launching browser')

    await stealth(page)
    site = 'https://www.zillow.com/' + place + '/fsbo'
    try:
        await page.goto(site, {'timeout': 10000})
    except Exception:
        raise Exception('Error loading page')

    await page.setViewport({"width": 1280, "height": 900})
    await asyncio.sleep(0.5)

    n = 0

    outfile = open(f_path, 'w', newline='')
    writer = csv.writer(outfile)
    writer.writerow(["Address", "bds", "ba", "price", "sqft", "Type", "lot", "yearbuilt", "overview", "link"])

    while True:
        await page.waitForSelector('#grid-search-results > ul > li:nth-child(5) > div > div')
        for pg_s in range(1, 7):
            await asyncio.sleep(0.3)
            try:
                await page.hover('#grid-search-results > ul > li:nth-child(' + str(7 * pg_s) + ') > div')
            except Exception:
                pass
        await asyncio.sleep(.5)
        try:
            html = await page.content()
        except Exception:
            raise Exception('Error loading page content')
        soup = BeautifulSoup(html, "html.parser")
        p_break = re.sub(",", "", soup.find('span', class_='result-count').text.strip(' results'))
        print(p_break + str(n))
        list_chk = soup.find_all('li',
                                 class_='ListItem-c11n-8-84-3__sc-10e22w8-0 StyledListCardWrapper-srp__sc-wtsrtn-0 iCyebE gTOWtl')
        print(len(list_chk))
        titles = soup.find_all('div',
                               class_='StyledPropertyCardDataWrapper-c11n-8-84-3__sc-1omp4c3-0 bKpguY property-card-data')
        list_1 = []
        list_2 = []
        list_3 = []
        list_4 = []
        for title in titles:
            price = title.find('span', class_='PropertyCardWrapper__StyledPriceLine-srp__sc-16e8gqd-1 iMKTKr').text
            p_data = title.find_all('li')
            if len(p_data) >= 3:
                bds = p_data[0].find('b').text
                ba = p_data[1].find('b').text
                area = p_data[2].find('b').text
            elif len(p_data) >= 2:
                bds = p_data[0].find('b').text
                ba = p_data[1].find('b').text
                area = 0
            elif len(p_data) >= 1:
                bds = p_data[0].find('b').text
                ba = 0
                area = 0
            else:
                ba = 0
                area = 0
                bds = 0

            addrs = title.find('address').text
            link = title.find('a')
            list_1.append(link['href'])
            list_2.append([addrs, bds, ba, price, area])

        tasks = [get_pg_info(listt) for listt in list_1]
        list_4 = await asyncio.gather(*tasks)
        list_3 = [s1 + s2 for s1, s2 in zip(list_2, list_4)]
        print(list_3)
        writer.writerows(list_3)
        n += len(titles)

        if int(p_break) <= n:
            print('Results Exceeded')
            break
        url1 = await page.evaluate("() => window.location.href")
        try:
            await asyncio.gather(
                page.waitForNavigation(),
                page.click('#grid-search-results > div.search-pagination > nav > ul > li:nth-child(10) > a')
            )

        except:
            await page.click('#grid-search-results > div.search-pagination > nav > ul > li:nth-child(10) > a')

        await asyncio.sleep(5)
        url2 = await page.evaluate("() => window.location.href")
        if url1 == url2:
            print('pages exceeded OR same page reload')
            break

    time.sleep(5)
    await browser.close()


async def get_pg_info(link):
    lst = await detail(link)
    return lst


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
