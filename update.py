import pandas as pd
import requests
import time
import datetime
from bs4 import BeautifulSoup
from gcp import write_df_to_bucket, get_file_from_bucket


def get_latest_fight_date(bucket_name: str) -> tuple[datetime, pd.DataFrame]:
    '''
    Getting latest date from our current dataset
    '''
    current_df = get_file_from_bucket(bucket_name, "Complete Stats.csv")
    current_df["dates"] = pd.to_datetime(current_df["dates"])

    return  current_df["dates"].max(), current_df

def get_latest_events(look_back: int = 500) -> list:
    '''
    Inital scrape of 'look_back' number of events.
    returns list of links
    '''
    r = requests.get("http://www.ufcstats.com/statistics/events/completed?page=all")
    soup = BeautifulSoup(r.content, 'html.parser')
    s = soup.find('section', class_ = 'b-statistics__section' )
    pages = s.find_all('a', class_ = 'b-link b-link_style_black')
    hrefs_start = [a['href'] for a in pages]
    hrefs_start = hrefs_start[0:look_back]
    return hrefs_start

def get_first_webpage_data(hrefs_start: list, latest_date: datetime) -> pd.DataFrame:
    '''
    Since all detailed stats are on a separate web page, we must
    filter the first 'summary' page by date and extract some fighter
    data here
    '''
    # Initializing variables
    stats_url = []
    fighter1=[]
    fighter2=[]
    weight = []
    method =[]
    rounds =[]
    times = []
    dates = []
    locations = []
    event = []
    index_value = 0

    url = hrefs_start[index_value]
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find('table')
    rows = table.find_all('tr')
    rows = rows[1:]
    for row in rows:
        date = soup.find('li', class_ = 'b-list__box-list-item')
        date = date.get_text(strip=True)[5:]
        date = pd.to_datetime(date)

    # Running while loop to find URLS before our latest date to avoid reading in duplicate data
    while date > latest_date:
        time.sleep(1)
        url = hrefs_start[index_value]
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        table = soup.find('table')
        rows = table.find_all('tr')
        rows = rows[1:]
        for row in rows:
            cols = row.find_all('td')
            data = [col.get_text(strip=True) for col in cols][6:]
            weight.append(data[0])
            method.append(data[1])
            rounds.append(data[2])
            times.append(data[3])
            fighters = row.find_all('a', class_ ="b-link b-link_style_black")
            names = [a.get_text(strip = True) for a in fighters]
            fighter1.append(names[0])
            fighter2.append(names[1])
            stat_link = row.get('data-link')
            
            if stat_link != '' or stat_link is not None:
                stats_url.append(row.get('data-link'))
            else: stats_url.append("No Link")

            location = soup.find_all('li', class_ = 'b-list__box-list-item')
            locations.append(location[1].get_text(strip=True)[9:])
            date = soup.find('li', class_ = 'b-list__box-list-item')
            date = date.get_text(strip=True)[5:]
            date = pd.to_datetime(date)
            dates.append(date)
            event.append(soup.find('h2').get_text(strip=True))
            index_value += 1
    
    new_df = pd.DataFrame({
        "stats_url" : stats_url,
        "fighter1" : fighter1,
        "fighter2" : fighter2,
        "weight" : weight,
        "method" : method,
        "rounds" : rounds,
        "times" : times,
        "dates" : dates,
        "locations" : locations,
        "event" : event
        })
    
    return new_df

def get_all_detailed_data(secondary_page_links: list) -> pd.DataFrame:
    '''
    Takes all links from fights that need to be added to data store and pulls
    all detailed information, logging and writing failures/failed request urls
    '''
    all_data = []
    failed_requests = []
    connect_timeout = 6
    read_timeout = 60
    success_count = 0
    failure_count = 0

    for url in secondary_page_links:
        try:
            time.sleep(1.5)
            r = requests.get(url, timeout=(connect_timeout, read_timeout))
            soup = BeautifulSoup(r.content, 'html.parser')
            max_round = soup.find_all("i", class_ = 'b-fight-details__text-item')
            max_round = max_round[2].get_text().split('Rnd')[0].strip()[-1]
            fight_details = soup.find_all('section', class_ = 'b-fight-details__section js-fight-section')
            fight_details = fight_details[1]
            tds = fight_details.find_all('td')
            row1 = []
            event = soup.find('h2').get_text(strip=True)
            for td in tds:
                p_tags = td.find_all('p')
                row1.append(p_tags[0].get_text(strip=True))
            f1 = row1[0]
            f1_kd = row1[1]
            f1_sigstr = row1[2]
            f1_sigstr_pct = row1[3]
            f1_totstr = row1[4]
            f1_td = row1[5]
            f1_td_pct = row1[6]
            f1_subatt = row1[7]
            f1_rev = row1[8]
            f1_ctrl = row1[9]
            row2 = []
            for td in tds:
                p_tags = td.find_all('p')
                row2.append(p_tags[1].get_text(strip=True))
            f2 = row2[0]
            f2_kd = row2[1]
            f2_sigstr = row2[2]
            f2_sigstr_pct = row2[3]
            f2_totstr = row2[4]
            f2_td = row2[5]
            f2_td_pct = row2[6]
            f2_subatt = row2[7]
            f2_rev = row2[8]
            f2_ctrl = row2[9]
            stats_url = url

            all_data.append({
                'fighter1' : f1,
                'fighter2': f2,
                'f1_kd' : f1_kd,
                'f1_sigstr' : f1_sigstr,
                'f1_sigstr_pct' : f1_sigstr_pct,
                'f1_totstr' : f1_totstr,
                'f1_td' : f1_td,
                'f1_td_pct' : f1_td_pct,
                'f1_subatt' : f1_subatt,
                'f1_rev' : f1_rev,
                'f1_ctrl' : f1_ctrl,
                'f2_kd' : f2_kd,
                'f2_sigstr' : f2_sigstr,
                'f2_sigstr_pct' : f2_sigstr_pct,
                'f2_totstr' : f2_totstr,
                'f2_td' : f2_td,
                'f2_td_pct' : f2_td_pct,
                'f2_subatt' : f2_subatt,
                'f2_rev' : f2_rev,
                'f2_ctrl' : f2_ctrl,
                'event' : event,
                'tot_round' : max_round,
                'stats_url' : stats_url
                })
            success_count += 1

        except Exception as e:
            failure_count += 1
            # How do we persist failed urls?
            dict_item = {'url': url, 'fail reason': e, 'date': datetime.now()}
            failed_requests.append(dict_item)

    response_stats = {}
    response_stats['successes'] = success_count
    response_stats['failures'] = failure_count
    print(response_stats)

    failed_requests = pd.DataFrame(failed_requests)

    if not failed_requests.empty:
        failed_requests.to_csv('failed_requests.csv', index=False, mode='a')
    
    new_stats_df = pd.DataFrame(all_data)

    return new_stats_df

def standardize_time_format(mmss):
    if mmss == '--':
        return 0
    else: minutes, seconds = map(int, mmss.split(":"))
    return (minutes*60) + seconds

def get_total_fight_time(row):
    remainder = standardize_time_format(row['times'])
    x = row['rounds'] - 1
    return (x*5*60) + remainder

def consolidate_methods(x):
    if "SUB" in x:
        return "SUB"
    elif "KO" in x:
        return "KO/TKO"
    elif "DEC" in x:
        return "DEC"
    else: 
        return "DQ/CNC/Overturned/Other"

def clean_and_prepare_final_df(detailed_df: pd.DataFrame, 
                               initial_df: pd.DataFrame) -> pd.DataFrame:
    '''
    clean data to enable analysis
    '''
    complete_df = initial_df.merge(detailed_df, on = ['stats_url', 'fighter1', 'fighter2', 'event'], how="left")

    # Typically ufc will place the winner in first index in detailed page, but not always
    # This checks that the join worked. sigstr should not be NULL
    mismatched_winner_df = complete_df[complete_df['f2_sigstr'].isna()]
    right_match = complete_df[~complete_df['f2_sigstr'].isna()]

    url_search = mismatched_winner_df['stats_url'].tolist()
    corrected_df = detailed_df[detailed_df['stats_url'].isin(url_search)]

    # Fixing so F1 will always be fight winner
    corrected_df = corrected_df.rename(columns={
        'fighter1' : 'fighter2',
        'fighter2': 'fighter1',
        'f1_kd' : 'f2_kd',
        'f1_sigstr' : 'f2_sigstr',
        'f1_sigstr_pct' : 'f2_sigstr_pct',
        'f1_totstr' : 'f2_totstr',
        'f1_td' : 'f2_td',
        'f1_td_pct' : 'f2_td_pct',
        'f1_subatt' : 'f2_subatt',
        'f1_rev' : 'f2_rev',
        'f1_ctrl' : 'f2_ctrl',
        'f2_kd' : 'f1_kd',
        'f2_sigstr' : 'f1_sigstr',
        'f2_sigstr_pct' : 'f1_sigstr_pct',
        'f2_totstr' : 'f1_totstr',
        'f2_td' : 'f1_td',
        'f2_td_pct' : 'f1_td_pct',
        'f2_subatt' : 'f1_subatt',
        'f2_rev' : 'f1_rev',
        'f2_ctrl' : 'f1_ctrl'
        })
    
    complete_df = pd.concat([corrected_df, right_match], ignore_index=True)
    print(f'total fights pulled: {len(complete_df)}')
    
    complete_df[['f1_sigstr_landed', 'f1_sigstr_attempt']] = complete_df['f1_sigstr'].str.split(' of ', expand=True).astype(int)
    complete_df[['f2_sigstr_landed', 'f2_sigstr_attempt']] = complete_df['f2_sigstr'].str.split(' of ', expand=True).astype(int)

    complete_df[['f1_totstr_landed', 'f1_totstr_attempt']] = complete_df['f1_totstr'].str.split(' of ', expand=True).astype(int)
    complete_df[['f2_totstr_landed', 'f2_totstr_attempt']] = complete_df['f2_totstr'].str.split(' of ', expand=True).astype(int)

    complete_df[['f1_td_landed', 'f1_td_attempt']] = complete_df['f1_td'].str.split(' of ', expand=True).astype(int)
    complete_df[['f2_td_landed', 'f2_td_attempt']] = complete_df['f2_td'].str.split(' of ', expand=True).astype(int)


    complete_df = complete_df.drop(columns=['f1_sigstr', 'f2_sigstr', 'f1_totstr', 'f2_totstr', 'f1_td', 'f2_td'])

    complete_df['f1_sigstr_pct'] = complete_df.apply(lambda row: row['f1_sigstr_landed']/row['f1_sigstr_attempt'] * 100 if row['f1_sigstr_attempt'] != 0 else 0, axis=1)
    complete_df['f2_sigstr_pct'] = complete_df.apply(lambda row: row['f2_sigstr_landed']/row['f2_sigstr_attempt'] * 100 if row['f2_sigstr_attempt'] != 0 else 0, axis=1)

    complete_df['f2_totstr_pct'] = complete_df.apply(lambda row: row['f2_totstr_landed']/row['f2_totstr_attempt'] * 100 if row['f2_totstr_attempt'] != 0 else 0, axis=1)
    complete_df['f1_totstr_pct'] = complete_df.apply(lambda row: row['f1_totstr_landed']/row['f1_totstr_attempt'] * 100 if row['f1_totstr_attempt'] != 0 else 0, axis=1)

    complete_df['f1_td_pct'] = complete_df.apply(lambda row: row['f1_td_landed']/row['f1_td_attempt'] * 100 if row['f1_td_attempt'] != 0 else 0, axis=1)
    complete_df['f2_td_pct'] = complete_df.apply(lambda row: row['f2_td_landed']/row['f2_td_attempt'] * 100 if row['f2_td_attempt'] != 0 else 0, axis=1)
        
    complete_df = complete_df[~complete_df['rounds'].isna()]
    complete_df['rounds'] = complete_df['rounds'].astype(int)
    
    complete_df['f1_ctrl_sec'] = complete_df['f1_ctrl'].apply(standardize_time_format)
    complete_df['f2_ctrl_sec'] = complete_df['f2_ctrl'].apply(standardize_time_format)

    complete_df['tot_fight_secs'] = complete_df.apply(get_total_fight_time, axis=1)

    complete_df['more_totstr_landed'] = complete_df.apply(lambda row: 'fighter1' if row['f1_totstr_landed'] > row['f2_totstr_landed'] else ('fighter2' if row['f1_totstr_landed'] < row['f2_totstr_landed'] else "equal"), axis=1)
    complete_df['more_totstr_attempt'] = complete_df.apply(lambda row: 'fighter1' if row['f1_totstr_attempt'] > row['f2_totstr_attempt'] else ('fighter2' if row['f1_totstr_attempt'] < row['f2_totstr_attempt'] else "equal"), axis=1)

    complete_df['more_sigstr_attempt'] = complete_df.apply(lambda row: 'fighter1' if row['f1_sigstr_attempt'] > row['f2_sigstr_attempt'] else ('fighter2' if row['f1_sigstr_attempt'] < row['f2_sigstr_attempt'] else "equal"),axis=1)
    complete_df['more_sigstr_landed'] = complete_df.apply(lambda row: 'fighter1' if row['f1_sigstr_landed'] > row['f2_sigstr_landed'] else ('fighter2' if row['f1_sigstr_landed'] < row['f2_sigstr_landed'] else "equal"),axis=1)

    return complete_df

def write_complete_stats(complete_df: pd.DataFrame,
                         current_df: pd.DataFrame,
                         bucket_name: str) -> None:
    '''
    writes complete stats table back to current dir
    '''
    new_total_stats = pd.concat([current_df, complete_df], ignore_index=True)

    new_total_stats['method'] = new_total_stats['method'].apply(consolidate_methods)

    new_total_stats.drop_duplicates(inplace=True)

    write_df_to_bucket(bucket_name, 'Complete Stats.csv', new_total_stats)

    # new_total_stats.to_csv("Complete Stats.csv", index=False)
    return

def write_normalized_stats(bucket_name) -> None:
    '''
    breaks down data so each fighter has their own row, then writes csv to dir
    '''
    stats_df = get_file_from_bucket(bucket_name, "Complete Stats.csv")
    f1_df = stats_df[['event', 'fighter1', 'weight', 'rounds',
       'times', 'method', 'locations', 'dates', 'stats_url', 'f1_kd',
       'f1_sigstr_pct', 'f1_td_pct', 'f1_subatt', 'f1_rev', 'f1_ctrl',
       'f1_sigstr_landed', 'f1_sigstr_attempt', 'f1_totstr_landed', 'f1_totstr_attempt', 'f1_td_landed',
       'f1_td_attempt',
       'f1_totstr_pct', 'f1_ctrl_sec', 'more_totstr_landed',
       'more_totstr_attempt', 'more_sigstr_attempt', 'more_sigstr_landed', 'tot_fight_secs', 'tot_round']].copy()

    f1_df["is_winner"] = True
    f1_df["fighter_num"] = "fighter1"

    f1_df.rename(columns={"fighter1" : "fighter" , 'f1_kd' : 'kd',
        'f1_sigstr_pct' : 'sigstr_pct', 'f1_td_pct' : 'td_pct', 'f1_subatt' : 'subatt', 'f1_rev' : 'rev', 'f1_ctrl' : 'ctrl', 'f1_sigstr_landed' : 'sigstr_landed',
        'f1_sigstr_attempt' : 'sigstr_attempt',
        'f1_totstr_landed' : 'totstr_landed', 'f1_totstr_attempt' : 'totstr_attempt', 'f1_td_landed' : 'td_landed', 'f1_td_attempt' : 'td_attempt', 'f1_totstr_pct' : 'totstr_pct', 'f1_ctrl_sec' : 'ctrl_sec'}, inplace=True)

    f2_df = stats_df[['event', 'fighter2', 'weight', 'rounds',
        'times', 'method', 'locations', 'dates', 'stats_url', 'f2_kd',
        'f2_sigstr_pct', 'f2_td_pct', 'f2_subatt', 'f2_rev', 'f2_ctrl', 'f2_sigstr_landed',
        'f2_sigstr_attempt',
        'f2_totstr_landed', 'f2_totstr_attempt', 'f2_td_landed', 'f2_td_attempt', 'f2_totstr_pct', 'f2_ctrl_sec', 'more_totstr_landed',
        'more_totstr_attempt', 'more_sigstr_attempt', 'more_sigstr_landed','tot_fight_secs','tot_round']].copy()

    f2_df["is_winner"] = False
    f2_df["fighter_num"] = "fighter2"

    f2_df.rename(columns={"fighter2" : "fighter", 
                        "f2_kd": "kd",
                        'f2_sigstr_pct': 'sigstr_pct',
                        'f2_td_pct': 'td_pct', 
                        'f2_subatt' : 'subatt', 
                        'f2_rev': 'rev', 'f2_ctrl': 'ctrl', 
                        'f2_sigstr_landed': 'sigstr_landed',
                        'f2_sigstr_attempt' : 'sigstr_attempt',
                        'f2_totstr_landed' : 'totstr_landed', 
                        'f2_totstr_attempt' : 'totstr_attempt', 
                        'f2_td_landed' : 'td_landed', 
                        'f2_td_attempt' : 'td_attempt',
                        'f2_totstr_pct' : 'totstr_pct', 
                        'f2_ctrl_sec' : 'ctrl_sec'}, inplace=True)
    
    norm_df = pd.concat([f1_df, f2_df], ignore_index = True)
    norm_df['method'] = norm_df['method'].apply(consolidate_methods)
    # norm_df.to_csv("Normalized Stats Table.csv", index=False)
    write_df_to_bucket(bucket_name, 'Normalized Stats Table.csv', norm_df)
    return
