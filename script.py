import csv
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as bs

req = Request(
    url='https://www.imdb.com/feature/genre/#movie', 
    headers={'User-Agent': 'Mozilla/5.0'}
)
webpage2 = urlopen(req).read()
soup2 = bs(webpage2,"html.parser")
genres = soup2.find_all('a', {'class': 'ipc-chip ipc-chip--on-base-accent2', 'href': lambda x: x and 'title_type=movie' in x})
# Variables to store the last successfully scraped genre and movie
last_genre = None
last_movie = None

# Create a CSV file and write header
csv_filename = 'movie_review.csv'
with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)

    # If last_genre and last_movie are not None, find their index in the 'genres' list
    if last_genre is not None and last_movie is not None:
        genre_index = next((i for i, genre in enumerate(genres) if genre.find('span', class_='ipc-chip__text').text == last_genre), None)
        if genre_index is not None:
            movie_index = next((i for i, movie in enumerate(genres[genre_index:].find_all('li', class_='ipc-metadata-list-summary-item')) if movie.find('div', class_='ipc-title ipc-title--base ipc-title--title ipc-title-link-no-icon ipc-title--on-textPrimary sc-43986a27-9 gaoUku dli-title').a.text.split('.')[1] == last_movie), None)

    # If either last_genre or last_movie is not found, start from the beginning
    if genre_index is None or movie_index is None:
        genre_index = 0
        movie_index = 0

    # Iterate through genres
    for genre in genres[genre_index:]:
        genre_name = genre.find('span', class_='ipc-chip__text').text
        genre_link = genre['href']

        req = Request(url='https://www.imdb.com' + genre_link, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        soup = bs(webpage, "html.parser")
        scraped_movies = soup.find_all('li', class_='ipc-metadata-list-summary-item')

        # Iterate through movies
        for movie in scraped_movies[movie_index:]:
            name = movie.find('div', class_='ipc-title ipc-title--base ipc-title--title ipc-title-link-no-icon ipc-title--on-textPrimary sc-43986a27-9 gaoUku dli-title').a.text.split('.')[1]

            # Skip movies with empty names
            if not name:
                continue

            # Iterate through reviews
            reviews_count = 0
            for a_tag in movie.find_all('a', href=True):
                url = a_tag['href']
                req = Request(url='https://www.imdb.com' + url, headers={'User-Agent': 'Mozilla/5.0'})
                page1 = urlopen(req).read()
                soup = bs(page1, "html.parser")
                review_scrap = soup.find('section', {'data-testid': 'UserReviews'})

                if review_scrap:
                    aatags = review_scrap.find_all('a', href=True)

                    if aatags:
                        review_url = aatags[0]['href']
                        if('tt_urv_add' in review_url):
                            # print(url)
                            continue
                        req = Request(url='https://www.imdb.com' + review_url, headers={'User-Agent': 'Mozilla/5.0'})
                        page2 = urlopen(req).read()
                        soup = bs(page2, "html.parser")
                        scraped_names = soup.find_all('div', class_='lister-item mode-detail imdb-user-review collapsable')

                        for username in scraped_names:
                            user_name = username.find('div', class_='lister-item-content').a.text
                            reviews_count += 1
                            csv_writer.writerow([genre_name, name, user_name])

                            if reviews_count == 10:
                                break

                if reviews_count == 10:
                    break

            # Update the last successfully scraped genre and movie
            last_genre = genre_name
            last_movie = name

        print(f'Successfully scraped genre: {genre_name} and movie: {name}')

    print(f'Data has been scraped and saved to {csv_filename}.')

#For better understanding of this code please go through the jupyter notebook