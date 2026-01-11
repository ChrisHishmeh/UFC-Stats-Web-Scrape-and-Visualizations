import pandas as pd


def get_all_tables():
    '''
    Function to pull csv file from directory, and return all dfs for use in the dash app
    '''
    df = pd.read_csv('Normalized Stats Table.csv')

    # Getting per second stats
    df['sigstr_per_sec'] = df['sigstr_landed']/df['tot_fight_secs']
    df['totstr_per_sec'] = df['totstr_landed']/df['tot_fight_secs']
    df['subatt_per_sec'] = df['subatt']/df['tot_fight_secs']

    df['rounds_round'] = df['tot_fight_secs']/300

    tot_fights = df.groupby(['fighter', 'weight']).size().reset_index(name = 'count')

    fighter_avgs = df.groupby(['fighter', 'weight'])[['is_winner', 'totstr_landed', 'sigstr_landed', 'ctrl_sec', 'sigstr_per_sec', 'totstr_per_sec', 'subatt_per_sec']].mean().reset_index()

    df_2 = fighter_avgs.merge(tot_fights, how='inner', on=['fighter', 'weight'])

    df_2['win_lose'] = df_2['is_winner'].apply(lambda x: 'green' if x >= 0.5 else "red")

    # Without weight class grouping
    tot_fights_nowc = df.groupby(['fighter','tot_round']).size().reset_index(name = 'count')

    fighter_avgs_nowc = df.groupby(['fighter','tot_round'])[['totstr_landed', 'sigstr_landed', 'ctrl_sec', 'is_winner', 'sigstr_per_sec', 'totstr_per_sec', 'subatt_per_sec', 'tot_fight_secs', 'td_landed']].mean().reset_index()

    df_3 = fighter_avgs_nowc.merge(tot_fights_nowc, how='inner', on=['fighter', 'tot_round'])

    df_3['win_lose'] = df_3['is_winner'].apply(lambda x: 'green' if x >= 0.5 else "red")
    round_cols1 = ['totstr_landed', 'sigstr_landed', 'ctrl_sec', 'subatt_per_sec', 'tot_fight_secs']
    round_cols2 = ['sigstr_per_sec', 'totstr_per_sec', 'is_winner']


    df_3[round_cols1] = round(df_3[round_cols1])
    df_3[round_cols2] = round(df_3[round_cols2], 2)


    table_data = df_3.rename(columns= {'tot_fight_secs': 'Avg Fight Time (secs)','fighter' : 'Fighter' ,'totstr_landed':'Avg Total Strikes Landed', 'sigstr_landed': 'Avg Significant Strikes Landed', 'ctrl_sec': 'Avg Control (secs)', 'is_winner' : 'Win Ratio',  'sigstr_per_sec': 'Avg Sig Strike Per Sec', 'totstr_per_sec' : 'Avg Total Strike Per Sec', 'count' : 'Count of UFC Fights', 'tot_round': 'Total Rounds', 'td_landed': 'Takedowns'})

    table_data = table_data.drop(columns = ['win_lose', 'subatt_per_sec'])
    table_data['Takedowns'] = table_data['Takedowns'].apply(lambda x: round(x,2))

    table_data = table_data[['Fighter','Total Rounds', 'Win Ratio', 'Count of UFC Fights', 'Avg Total Strikes Landed', 'Avg Significant Strikes Landed', 'Avg Control (secs)', 'Avg Sig Strike Per Sec', 'Avg Total Strike Per Sec', 'Avg Fight Time (secs)', 'Takedowns']]

    df_3.rename(columns= {'tot_fight_secs': 'Fight Time (s)','fighter' : 'Fighter' ,'totstr_landed':'Total Strikes Landed', 'sigstr_landed': 'Significant Strikes Landed', 'ctrl_sec': 'Control Time (s)', 'is_winner' : 'Win Ratio',  'sigstr_per_sec': 'Sig Strike Per Sec', 'totstr_per_sec' : 'Total Strike Per Sec', 'count' : 'Count of UFC Fights'}, inplace=True)

    df_2.rename(columns= {'is_winner' : 'Win Ratio','tot_fight_secs': 'Fight Time (s)','fighter' : 'Fighter' ,'totstr_landed':'Total Strikes Landed', 'sigstr_landed': 'Significant Strikes Landed', 'ctrl_sec': 'Control Time (s)', 'sigstr_per_sec': 'Sig Strike Per Sec', 'totstr_per_sec' : 'Total Strike Per Sec', 'count' : 'Count of UFC Fights'}, inplace=True)

    # Primary win method
    wins_method = df[df['is_winner'] == True]
    wins_method  = wins_method .groupby(['weight'])[['totstr_landed', 'sigstr_landed', 'ctrl_sec', 'is_winner', 'sigstr_per_sec', 'totstr_per_sec', 'subatt_per_sec']].mean().reset_index()
    wins_method.rename(columns= {'is_winner' : 'Win Ratio', 'tot_fight_secs': 'Fight Time (s)','fighter' : 'Fighter' ,'totstr_landed':'Total Strikes Landed', 'sigstr_landed': 'Significant Strikes Landed', 'ctrl_sec': 'Control Time (s)', 'sigstr_per_sec': 'Sig Strike Per Sec', 'totstr_per_sec' : 'Total Strike Per Sec', 'count' : 'Count of UFC Fights'}, inplace=True)
    # Primary lose method
    lose_method = df[df['is_winner'] == False]
    lose_method  = lose_method .groupby(['weight'])[['totstr_landed', 'sigstr_landed', 'ctrl_sec', 'is_winner', 'sigstr_per_sec', 'totstr_per_sec', 'subatt_per_sec']].mean().reset_index()
    lose_method.rename(columns= {'is_winner' : 'Win Ratio','tot_fight_secs': 'Fight Time (s)','fighter' : 'Fighter' ,'totstr_landed':'Total Strikes Landed', 'sigstr_landed': 'Significant Strikes Landed', 'ctrl_sec': 'Control Time (s)',  'sigstr_per_sec': 'Sig Strike Per Sec', 'totstr_per_sec' : 'Total Strike Per Sec', 'count' : 'Count of UFC Fights'}, inplace=True)

    # For fighter comparison - count of method for each fighter wins with or lost to
    df_winner = df[df['is_winner'] == True].groupby(['fighter', 'method']).size().reset_index(name = 'win count')
    df_winner =  df[df['is_winner'] == True].groupby(['fighter', 'method', 'tot_round']).size().reset_index(name = 'win count')
    df_winner3 = df_winner[df_winner['tot_round'] == '3']
    df_winner5 = df_winner[df_winner['tot_round'] == '5']

    df_loser = df[df['is_winner'] == False].groupby(['fighter', 'method', 'tot_round']).size().reset_index(name = 'lose count')
    df_loser3 = df_loser[df_loser['tot_round'] == '3']
    df_loser5 = df_loser[df_loser['tot_round'] == '5']

    # Drop down option values
    fighter_names = sorted(df['fighter'].unique())
    weight_classes = sorted(df['weight'].unique())

    return df, df_2, df_3, table_data, wins_method, lose_method, df_winner, \
        df_loser, df_winner5, df_winner3, df_loser3, df_loser5, fighter_names, weight_classes