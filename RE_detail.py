import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup
from pyppeteer_stealth import stealth

path = '/Users/trishika/PycharmProjects/pythonProject'


async def main():
    await detail(site='www.example.com')


async def detail(site):
    browser = await launch({'headless': True})
    print(site)
    page = await browser.newPage()
    await stealth(page)

    await page.goto(site, {'waitUntil': 'domcontentloaded', 'timeout': 0})
    html2 = await page.content()
    data_p = []
    # print(html2)
    soup1 = BeautifulSoup(html2, "html.parser")
    type_p = 0
    lot_p = 0
    year_p = 0
    listes = soup1.find_all('li', class_='AtAGlanceFact__StyledFact-sc-2arhs5-0 jKDFoe')
    for liste in listes:
        if liste.find('title').text == "Type":
            type_p = liste.find('span',
                                class_='Text-c11n-8-84-3__sc-aiai24-0 AtAGlanceFact__StyledfactValue-sc-2arhs5-3 hrfydd iYUreA').text
        if liste.find('title').text == "Lot":
            lot_p = liste.find('span',
                               class_='Text-c11n-8-84-3__sc-aiai24-0 AtAGlanceFact__StyledfactValue-sc-2arhs5-3 hrfydd iYUreA').text
        if liste.find('title').text == "Year Built":
            year_p = liste.find('span',
                                class_='Text-c11n-8-84-3__sc-aiai24-0 AtAGlanceFact__StyledfactValue-sc-2arhs5-3 hrfydd iYUreA').text

    try:
        overview = soup1.find('div', class_='Text-c11n-8-84-3__sc-aiai24-0 sc-IQBGL hrfydd jxhRtC').text
    except:
        overview = 0

    data_p.extend([type_p, lot_p, year_p, overview, site])
    await browser.close()
    return data_p


if __name__ == '__main__':
    asyncio.run(main())
