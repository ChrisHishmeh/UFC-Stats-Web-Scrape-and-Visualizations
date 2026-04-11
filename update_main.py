from update import get_latest_fight_date, get_latest_events, \
            get_first_webpage_data, get_all_detailed_data, clean_and_prepare_final_df, \
            write_complete_stats, write_normalized_stats

def main():
    print('Starting get_latest_fight_date')
    latest_date, current_df = get_latest_fight_date()
    print('Completed get_lates_fight_date')

    print('Starting get_latest_events')
    primary_links = get_latest_events()
    print('Completed get_latest_events')

    print('Starting get_first_webpage_data')
    initial_df = get_first_webpage_data(primary_links, latest_date)
    print('Completed get_first_webpage_data')

    print('Starting get_all_detailed_data')
    detailed_df = get_all_detailed_data(initial_df['stats_url'])
    print('Completed get_all_detailed_data')

    print('Cleaning and preparing final dataframe')
    complete_df = clean_and_prepare_final_df(detailed_df, initial_df)

    print('Writing complete stats')
    write_complete_stats(complete_df, current_df)

    print('Writing normalized stats')
    write_normalized_stats()

    return

if __name__ == '__main__':
    try:
        print('Program started')
        main()
    except Exception as e:
        print('Program crashed')
        print(f'Error occured in update_main.py: {e}')
        import traceback
        import sys
        tb = traceback.extract_tb(sys.exc_info()[2])
        last_frame = tb[-1]
        file = last_frame[0]
        line_no = last_frame[1]
        func_name = last_frame[2]
        print(f'File: {file} \nLine: {line_no} \nFunction: {func_name}')

