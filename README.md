# Overview
View deployed app here (https://ufc-stats-visualizations.onrender.com)
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

# Deployment

## Docker Steps
1. Once code is finalized, create local docker image using command
    `docker build -t {local-image-name} .`

2. Ensure that the artifact repo already exists in gcp. If it doesn't exist, create repo using:
    `gcloud artifacts repositories create {repo name} --repository-format=docker --location={region}`


3. Tag image with gcp region and artifact repository name. Run command
    `docker tag {local-image-name} {REGION-docker.pkg.dev/PROJECT ID/ARTIFACT REPO/NAME}`
    ensure that the artifact repo already exists in gcp.

4. Authenticate docker to allow push to GCP (modifies docker config)
    `gcloud auth configure-docker {REGION-docker.pkg.dev}`   

5. Push container to GCP artifact registry
    `docker push {longer rename from step 3}`

6. Ensure that service account has correct IAM permissions for buckets. Ensure right files are in bucket to read and write


## Architecture
2 csv files exist in GCP storage. A python script (`update_main.py`) refreshes these files by pulling down the existing files from gcp storage and performing an initial/probe scrape of the stats website to determine if the csv files need to be refreshed. If there is new data to scrape, we run the rest of the update file and overwrite the files in gcp storage with a new csv that contains updated stats data.
The refresh script is containerized via docker and will be deployed as a job on a cron schedule hosted in gcp.