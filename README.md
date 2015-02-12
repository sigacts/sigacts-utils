# sigacts-utils

### batchCreateSrc.py
Ingest a batch of URLs and output clean "source" domains.
> Example: `http://www.cnn.com/2015/02/12/europe/ukraine-conflict/index.html` becomes `cnn.com`

## diffBot.py
Extracts data from a news article using [Diffbot](https://www.diffbot.com/).

## findDate.py
Check a URL to see if it provides a clue about the date an article was published.

## processArticle.py
Given a URL, extract data from a page using the [Readability Pareser API](https://readability.com/developers/api), then search it for geo references using the Yahoo PlaceFinder API.

## processRSSFeed.py
Ingest an RSS feed and push each entry into a database. There is conditional handling for lots of different date formats.

## sigTools.py
This is a general utility to wrap the database connection and handle other odds and ends.
