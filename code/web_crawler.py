import requests
import bs4
from bs4 import BeautifulSoup as soup
import pandas as pd
import time

def start_crawl():
    print("\nWelcome to 'My First Web Crawler' by Miasia Jones")

    df = pd.DataFrame(columns = ['title', 'date', 'url', 'html_content'])
    queue_stats_df = pd.DataFrame(columns = ['elaped_time', 'pages_queued'])
    visited_stats_df = pd.DataFrame(columns = ['elaped_time', 'pages_visited'])

    url_queue = []
    visited_urls = []

    # initializing seed URL
    seed_url = 'https://www.cc.gatech.edu/news/1'

    print("\nSetting seed URL to {}".format(seed_url))

    # get number of pages
    first_page = requests.get(seed_url)
    first_page_soup = soup(first_page.text, "html.parser")
    last_page = first_page_soup.find_all("li", {"class":"pager-last last"})[0].a["href"]
    number_of_pages = int(last_page.partition("page=")[2]) + 1

    print("\n[STARTING CRAWLER]\n")

    ### QUEUING URLS ###
    print("Finding how many URLs are linked to seed URL...")

    t = time.time()

    for i in range(1, number_of_pages):
        page_number = i

        if page_number == 1:
            page = requests.get(seed_url)
        else:
            page = requests.get(seed_url + '?page=' + str(page_number))

        page_soup = soup(page.text, "html.parser")
        
        # get containers of article information
        class_names = ['views-row-odd views-row-first news-page-row', 
                    'views-row-even news-page-row', 
                    'views-row-odd news-page-row', 
                    'views-row-even views-row-last news-page-row']
        
        all_containers = []
        for class_name in class_names:
            for container in page_soup.find_all("div", {"class":class_name}):
                all_containers.append(container)

        visited_urls.append(page)

        for container in all_containers:
            title_container = container.find_all("h3", {"class": "news-title"})
            article_url = 'https://www.cc.gatech.edu' + title_container[0].a["href"]
            url_queue.append(article_url)

            queue_stats_df = queue_stats_df.append({'elaped_time':format(time.time() - t, '.2f'), 'pages_queued':len(url_queue)}, ignore_index=True)

    print("Found {} URLs linked to seed URL".format(len(url_queue)))

    ### VISITING URLS ###
    t = time.time()

    for j, article_url in enumerate(url_queue):
        article_number = j + 1

        if article_url not in visited_urls:
            article_page = requests.get(article_url)
            article_page_soup = soup(article_page.text, "html.parser")

            # get article information
            article_date_container = article_page_soup.find_all("span", {"class":"date-display-single"})
            if len(article_date_container) != 0:
                article_date = article_date_container[0].text
            else:
                article_date = None

            article_title = article_page_soup.find_all("h2", {"class": "title"})[0].text

            main_content = article_page_soup.find_all("section", {"id":"main"})[0]
            
            # outputting to console
            print("Crawling URL {} / {}".format(article_number, len(url_queue)), end="\r")

            visited_urls.append(article_url)
            df = df.append({'title':article_title, 'date':article_date, 'url': article_url, 'html_content': main_content}, ignore_index=True)


        visited_stats_df = visited_stats_df.append({'elaped_time':format(time.time() - t, '.2f'), 'pages_visited':len(visited_urls)}, ignore_index=True)

    print("\nFinished crawling ---- Time Elapsed: {:.2f} s".format(time.time() - t))
    # format article date column in df
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.sort_values(by=['date'], ascending=False)

    # convert dfs to csv for later use
    df.to_csv('../data/articles.csv')
    queue_stats_df.to_csv('../data/queue_stats.csv')
    visited_stats_df.to_csv('../data/visited_stats.csv')

    print("\n[CRAWLING COMPLETE]\n")

if __name__ == "__main__":
    start_crawl()
