import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, callback, Patch, dash_table
import dash_bootstrap_components as dbc

app = Dash(__name__, suppress_callback_exceptions = True)
server = app.server

# Preparing data to load into visuals
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

fighter_avgs_nowc = df.groupby(['fighter','tot_round'])[['totstr_landed', 'sigstr_landed', 'ctrl_sec', 'is_winner', 'sigstr_per_sec', 'totstr_per_sec', 'subatt_per_sec', 'tot_fight_secs']].mean().reset_index()

df_3 = fighter_avgs_nowc.merge(tot_fights_nowc, how='inner', on=['fighter', 'tot_round'])

df_3['win_lose'] = df_3['is_winner'].apply(lambda x: 'green' if x >= 0.5 else "red")
round_cols1 = ['totstr_landed', 'sigstr_landed', 'ctrl_sec', 'subatt_per_sec', 'tot_fight_secs']
round_cols2 = ['sigstr_per_sec', 'totstr_per_sec', 'is_winner']


df_3[round_cols1] = round(df_3[round_cols1])
df_3[round_cols2] = round(df_3[round_cols2], 2)


table_data = df_3.rename(columns= {'tot_fight_secs': 'Avg Fight Time (secs)','fighter' : 'Fighter' ,'totstr_landed':'Avg Total Strikes Landed', 'sigstr_landed': 'Avg Significant Strikes Landed', 'ctrl_sec': 'Avg Control (secs)', 'is_winner' : 'Win Ratio',  'sigstr_per_sec': 'Avg Sig Strike Per Sec', 'totstr_per_sec' : 'Avg Total Strike Per Sec', 'count' : 'Count of UFC Fights', 'tot_round': 'Total Rounds'})

table_data = table_data.drop(columns = ['win_lose', 'subatt_per_sec'])

table_data = table_data[['Fighter','Total Rounds', 'Win Ratio', 'Count of UFC Fights', 'Avg Total Strikes Landed', 'Avg Significant Strikes Landed', 'Avg Control (secs)', 'Avg Sig Strike Per Sec', 'Avg Total Strike Per Sec', 'Avg Fight Time (secs)']]

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


# USER INTERFACE
app.layout = html.Div([
                    html.Div(style={
                    'padding': '10px',
                    'textAlign': 'center',
                    'backgroundColor': "#d5ebfd",
                    'border': '1px solid black',
                    'fontFamily': 'Open Sans, sans-serif'
                }, children = [
                html.H1('UFC FIGHT STATS', style={'textAlign': 'center'})]),
    dcc.Tabs(id = 'tabs', value = 'tab-1', children =[
        dcc.Tab(label = "General Stats", value = 'tab-1', style = {
            'border' : '1px solid #1a1a1a',
            'backgroundColor' : "#d5ebfd",
            'fontFamily': 'Open Sans, sans-serif',
            'fontSize': '25px'
        }, selected_style= {
            'fontWeight' : 'bold',
            'border' : '1px solid #1a1a1a',
            'fontFamily': 'Open Sans, sans-serif',
            'fontSize': '30px'
        }),
        dcc.Tab(label = 'Fighter Comparison', value = 'tab-2', style = {
            'border' : '1px solid #1a1a1a',
            'backgroundColor' : "#d5ebfd",
            'fontFamily': 'Open Sans, sans-serif',
            'fontSize': '25px'
        }, selected_style= {
            'fontWeight' : 'bold',
            'border' : '1px solid #1a1a1a',
            'fontFamily': 'Open Sans, sans-serif',
            'fontSize': '30px'
        })]),
       # html.Div(id = 'tab-content'),
        html.Div(id = 'tab1', style = {'display':'flex', 'flexDirection':'column', 'display' : 'block'}, children=[
                html.Div(style = {
                    'display': 'flex'
                }, children = [
                    html.Div(style = {
                        'width': '20%',
                        'padding' : '5px',
                        'border': '1px solid black',
                        'fontFamily': 'Open Sans, sans-serif'
                    }, children = [
                        html.H1("Filters"),
                        # html.P("Fighter", style={'fontWeight': 'Bold'}),
                        # dcc.Dropdown(id = 'fighter-name', options = [{'label': fighter, 'value': fighter} for fighter in fighter_names], value = 'Charles Oliveira'),
                        html.P("Stat", style={'fontWeight': 'Bold'}),
                        dcc.Dropdown(id = 'metric', options = ['Fight Time (s)','Total Strikes Landed', 'Significant Strikes Landed','Control Time (s)', 'Win Ratio', 'Sig Strike Per Sec', 'Total Strike Per Sec', 'Count of UFC Fights'], value = 'Total Strikes Landed', clearable=False),
                        html.P("Weight Class", style={'fontWeight': 'Bold'}),
                        dcc.Dropdown(id = 'weight-class-filter', options = [{'label': wc, 'value':wc} for wc in weight_classes], value = 'Lightweight'),
                        html.P("Minimum # of Fights in the UFC", style={'fontWeight': 'Bold'}),
                        dcc.Slider(id= 'fighter-experience', min = 0, max = 15, step = 1, value = 5)
                    ]),

                    html.Div(style = {
                        'width': '80%',
                        'padding' : '5px',
                        'border': '1px solid black',
                        'gap' : '10px',
                        'fontFamily': 'Open Sans, sans-serif'
                    }, children = [
                        dcc.Graph(id = 'avgs-chart'),
                        dcc.Graph(id = 'gbar'),
                        dash_table.DataTable(
                            id = 'fighter-table',
                            columns = [{'name': col, 'id': col} for col in table_data.columns],
                            data = table_data.to_dict('records'),
                            style_table = {'overflowX': 'auto'},
                            style_cell = {'textAlign': 'left',
                                        'fontFamily': 'Open Sans, sans-serif',
                                        'height' : 'auto',
                                        'whiteSpace' : 'normal'},
                            style_header = {
                                        'backgroundColor' : "#d5ebfd",
                                        'fontWeight' : 'bold',
                                        'textAlign': 'center'
                            },
                            page_size = 5,
                            filter_action= 'native'
                        )
                    ])])
            ]),
            html.Div(id = 'tab2', style = {'display':'flex', 'display': 'none', 'flexDirection': 'row'},children=[
            html.Div(style = {
                        'padding' : '5px',
                       # 'border': '1px solid black',
                        'fontFamily': 'Open Sans, sans-serif',
                        'width' : '48%', 
                        'display': 'inline-block'
                    }, children = [
                        dcc.RadioItems(id  = 'round-nums-filter', options=['3 Rounds', '5 Rounds', 'All'], value = '3 Rounds', inline = True, style={'fontSize': '20px', 'padding': '10px'}),
                        dcc.Dropdown(id = 'fighter1-name', options = fighter_names, style= {'width': '400px', 'fontWeight': 'bold', 'fontSize': '25px'}),
                        dcc.Graph(id = 'method-bar1'),
                        dcc.Graph(id = 'rounds-hist-1'),
                        dash_table.DataTable(
                            id = 'fighter-table1',
                            columns = [{'name': col, 'id': col} for col in table_data.columns],
                            data = table_data.to_dict('records'),
                            style_table = {'overflowX': 'auto'},
                            style_cell = {'textAlign': 'left',
                                        'fontFamily': 'Open Sans, sans-serif',
                                        'height' : 'auto',
                                        'whiteSpace' : 'normal'},
                            style_header = {
                                        'backgroundColor' : "#d5ebfd",
                                        'fontWeight' : 'bold',
                                        'textAlign': 'center'
                            },
                            page_size = 5)
                            ]),
            html.Div(style = {
                        'padding' : '15px',
                        #'border': '1px solid black',
                        'fontFamily': 'Open Sans, sans-serif',
                        'width' : '48%', 
                        'display': 'inline-block'
                        }, children = [
                            dcc.Dropdown(id = 'fighter2-name', options = fighter_names, style= {'width': '400px', 'fontWeight': 'bold', 'fontSize': '25px'}),
                            dcc.Graph(id = 'method-bar2'),
                            dcc.Graph(id = 'rounds-hist-2'),
                            dash_table.DataTable(
                            id = 'fighter-table2',
                            columns = [{'name': col, 'id': col} for col in table_data.columns],
                            data = table_data.to_dict('records'),
                            style_table = {'overflowX': 'auto'},
                            style_cell = {'textAlign': 'left',
                                        'fontFamily': 'Open Sans, sans-serif',
                                        'height' : 'auto',
                                        'whiteSpace' : 'normal'},
                            style_header = {
                                        'backgroundColor' : "#d5ebfd",
                                        'fontWeight' : 'bold',
                                        'textAlign': 'center'
                            },
                            page_size = 5)
                            ])
                        
            ])
    ])

# Callbacks
@app.callback(
        Output('tab1', 'style'),
        Output('tab2', 'style'),
        Input('tabs', 'value')
)

def display_tab(tab):
    if tab == 'tab-1':
        return {'display': 'block'}, {'display': 'none'}
    elif tab == 'tab-2':
        return {'display': 'none'}, {'display': 'inline-block'}




@app.callback(
    Output('avgs-chart', 'figure'),
    Output('gbar', 'figure'),
    # Input('fighter-name', 'value'),
    Input('weight-class-filter', 'value'),
    Input('fighter-experience', 'value'),
    Input('metric', 'value')
)

def filter_general_stats(selected_wc, fighter_experience, metric):
    
    # if name is None:
    #     filt_df = df_3
    #     fight_name_title = "Fighter"
    # else: 
    #     filt_df = df_2[df_2['fighter'] == name]
    #     fight_name_title = name

    if selected_wc is None:
        filt_df2 = df_3
        bar_title = "All"
    else: 
        filt_df2 = df_2[df_2['weight'] == selected_wc]
        bar_title = selected_wc

    filt_df3 = filt_df2[filt_df2['Count of UFC Fights'] >= fighter_experience]

    filt_df3 = filt_df3.sort_values(by = metric, ascending = False)
    
    # Bar plot development
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x = filt_df3['Fighter'],
        y = filt_df3[metric],
        marker_color = filt_df3['win_lose'],
        customdata = filt_df3[['Win Ratio']],
        hovertemplate = "<b>%{x}</b><br><b>Value: </b>%{y}<br><b>Win Ratio: </b>%{customdata[0]:.0%}<extra></extra>"
    ))

    fig.update_layout(
        title = f'Average Number of {metric} by Fighter in {bar_title}',
        xaxis_title = 'Fighter',
        yaxis_title = f"Average {metric}",
        xaxis_tickangle = -45,
        height = 525
    )
    
    avg_line = round(filt_df3[metric].mean())

    fig.add_hline(
        y = avg_line,
        line_color = 'black',
        annotation_text = f"Average: {avg_line}",
        annotation_position = 'top right'
    )

    # Scatter plot development
    # scatterplot = px.scatter(
    #     filt_df2, x = metric, y = 'is_winner', title = f"Win ratio vs. Avg {metric}", color_discrete_sequence= ['black'], hover_data=['fighter']
    # )
    # scatterplot.update_layout(
    #     yaxis_title = 'Win %',
    #     xaxis_title = f'Average {metric}',
    #     shapes=[
    #         dict(
    #             type='rect',
    #             xref='paper', yref = 'y',
    #             x0=0, x1=1,y0=0.5,y1=1,
    #             fillcolor = 'lightgreen', opacity=0.3, line_width=0
    #         ),
    #         dict(
    #             type='rect',
    #             xref='paper', yref = 'y',
    #             x0=0, x1=1,y0=0,y1=0.5,
    #             fillcolor = 'lightcoral', opacity=0.3, line_width=0
    #         )
    #     ]
    # ) RETURN scatterplot

    # Grouped Bar Chart Develompent
    grouped_bar = go.Figure(data=[go.Bar(
    name = 'Win',
    x = wins_method['weight'],
    y = wins_method[metric],
    marker_color = 'green'
   ),
                       go.Bar(
    name = 'Loss',
    x = lose_method['weight'],
    y = lose_method[metric],
    marker_color = 'red'
   )
    ])
    grouped_bar.update_layout(
        title = f'Average Number of {metric} by Weight Class and Fight Outcome',
        xaxis_title = 'Weight Class',
        yaxis_title = f"Average {metric}",
        xaxis_tickangle = -45,
        height = 525
    )
 

    return fig, grouped_bar

@app.callback(
    Output('method-bar1', 'figure'),
    Output('method-bar2', 'figure'),
    Output('rounds-hist-1', 'figure'),
    Output('rounds-hist-2', 'figure'),
    Output('fighter-table1', 'data'),
    Output('fighter-table2', 'data'),
    Input('round-nums-filter', 'value'),
    Input('fighter1-name', 'value'),
    Input('fighter2-name', 'value'),
)


def filter_fighter_comparison(rounds, fighter1, fighter2):
    if rounds == '3 Rounds':
        f1_win = df_winner3[df_winner3['fighter'] == fighter1]
        f2_win = df_winner3[df_winner3['fighter'] == fighter2]
        f1_lose = df_loser3[df_loser3['fighter'] == fighter1]
        f2_lose = df_loser3[df_loser3['fighter'] == fighter2]
        hist_data = df[df['tot_round'] == '3']
        end_interval = 3
        table_data_show = table_data[table_data['Total Rounds'] == '3']
    elif rounds == '5 Rounds':
        f1_win = df_winner5[df_winner5['fighter'] == fighter1]
        f2_win = df_winner5[df_winner5['fighter'] == fighter2]
        f1_lose = df_loser5[df_loser5['fighter'] == fighter1]
        f2_lose = df_loser5[df_loser5['fighter'] == fighter2]
        hist_data = df[df['tot_round'] == '5']
        end_interval = 5
        table_data_show = table_data[table_data['Total Rounds'] == '5']
    else:
        f1_win = df_winner[df_winner['fighter'] == fighter1]
        f2_win = df_winner[df_winner['fighter'] == fighter2]
        f1_lose = df_loser[df_loser['fighter'] == fighter1]
        f2_lose = df_loser[df_loser['fighter'] == fighter2]
        table_data_show = table_data
        hist_data = df
        end_interval = 5
    
    fig1 = go.Figure(data = [
        go.Bar(name = 'Wins', x = f1_win['method'], y = f1_win['win count'], marker = dict(color = 'green')),
        go.Bar(name = 'Loss', x = f1_lose['method'], y = f1_lose['lose count'], marker = dict(color = 'red'))
    ])
    fig1.update_layout(
        title = f"{fighter1}'s Wins by Method",
        xaxis_title = 'Method',
        yaxis_title = "Count",
        xaxis_tickangle = -45
    )

    fig2 = go.Figure(data = [
        go.Bar(name = 'Wins', x = f2_win['method'], y = f2_win['win count'], marker = dict(color = 'green')),
        go.Bar(name = 'Loss', x = f2_lose['method'], y = f2_lose['lose count'], marker = dict(color = 'red'))
    ])
    fig2.update_layout(        title = f"{fighter1}'s Wins by Method ({rounds})",
        xaxis_title = 'Method',
        yaxis_title = "Count",
        xaxis_tickangle = -45
    )

    fig2.update_layout(
        title = f"{fighter2}'s Wins by Method ({rounds})",
        xaxis_title = 'Method',
        yaxis_title = "Count",
        xaxis_tickangle = -45
    )

    hist1 = hist_data[hist_data['fighter'] == fighter1]
    hist1 = go.Figure(go.Histogram(
            x = hist1['rounds_round'],
            xbins=dict(
                start=0, end=end_interval, size=0.5
            ), 
            autobinx=False,
            marker = dict(line = dict(
                color = 'black',
                width=1
            ))
        ))
    hist1.update_layout(
        title = f"{fighter1}'s Fight Length Distribution ({rounds})",
        xaxis_title = 'Length of Fight (Intervals of 0.5 Round)',
        yaxis_title = 'Count'
    )
    
    hist2 = hist_data[hist_data['fighter'] == fighter2]
    hist2 = go.Figure(go.Histogram(
            x = hist2['rounds_round'],
            xbins=dict(
                start=0, end=end_interval, size=0.5
            ), 
            autobinx=False,
            marker = dict(line = dict(
                color = 'black',
                width=1
            ))
        ))
    hist2.update_layout(
        title = f"{fighter2}'s Fight Length Distribution ({rounds})",
        xaxis_title = 'Length of Fight (Intervals of 0.5 Round)',
        yaxis_title = 'Count'
    )


    fighter1_table = table_data_show[table_data_show['Fighter'] == fighter1]
    fighter2_table = table_data_show[table_data_show['Fighter'] == fighter2]


    return fig1, fig2, hist1, hist2, fighter1_table.to_dict('records'), fighter2_table.to_dict('records')



if __name__ == '__main__':
    app.run(debug = True)