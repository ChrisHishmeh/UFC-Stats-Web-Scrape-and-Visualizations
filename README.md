# UFC-Stats-Web-Scrape-and-Visualizations
Python data pipeline designed to scrape stats data from UFC's official stats website (http://www.ufcstats.com/statistics/events/completed), clean and transform this data, load this data into a dash app for interactive visualizations, and incrementally refresh when new fights stats are published on the website. 

 **Inital Scrape**
The initial scrape py file is to be ran first, and pulls down all fights from the website (~7k rows, or fights)

**Refresh Script**
The Refresh script checks the for the latest date in the csv file, and then only pulls in data after that date, adding new, recent data to the CSV file.

**Visualization App**
The visualization app is an app created using the Dash library that runs locally. This app visualizes the normalized data and allows for user interaction.

**CSVs**
There are two main CSV outputs: Complete Stats.csv and Normalized Stats Table.csv

Complete Stats is preprocessed data. 1 row represents a single fight for 2 athletes. It is not used in the app.

Normalized Stats Table is processed and normalized. 1 row represents 1 fight for a single athlete. This data is used in the app.
