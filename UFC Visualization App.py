import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, callback, Patch, dash_table
import dash_bootstrap_components as dbc

app = Dash()

# Preparing data to load into visuals
df = pd.read_csv('Normalized Stats Table.csv')

# Getting per second stats
df['sigstr_per_sec'] = df['sigstr_landed']/df['tot_fight_secs']
df['totstr_per_sec'] = df['totstr_landed']/df['tot_fight_secs']
df['subatt_per_sec'] = df['subatt']/df['tot_fight_secs']

tot_fights = df.groupby(['fighter', 'weight']).size().reset_index(name = 'count')

fighter_avgs = df.groupby(['fighter', 'weight'])[['totstr_landed', 'sigstr_landed', 'ctrl_sec', 'is_winner', 'sigstr_per_sec', 'totstr_per_sec', 'subatt_per_sec']].mean().reset_index()

df_2 = fighter_avgs.merge(tot_fights, how='inner', on=['fighter', 'weight'])

df_2['win_lose'] = df_2['is_winner'].apply(lambda x: 'green' if x >= 0.5 else "red")

# Without weight class grouping
tot_fights_nowc = df.groupby(['fighter']).size().reset_index(name = 'count')

fighter_avgs_nowc = df.groupby(['fighter'])[['totstr_landed', 'sigstr_landed', 'ctrl_sec', 'is_winner', 'sigstr_per_sec', 'totstr_per_sec', 'subatt_per_sec', 'tot_fight_secs']].mean().reset_index()

df_3 = fighter_avgs_nowc.merge(tot_fights_nowc, how='inner', on=['fighter'])

df_3['win_lose'] = df_3['is_winner'].apply(lambda x: 'green' if x >= 0.5 else "red")
round_cols1 = ['totstr_landed', 'sigstr_landed', 'ctrl_sec', 'subatt_per_sec', 'tot_fight_secs']
round_cols2 = ['sigstr_per_sec', 'totstr_per_sec', 'is_winner']


df_3[round_cols1] = round(df_3[round_cols1])
df_3[round_cols2] = round(df_3[round_cols2], 2)


table_data = df_3.rename(columns= {'tot_fight_secs': 'Avg Fight Time (secs)','fighter' : 'Fighter' ,'totstr_landed':'Avg Total Strikes Landed', 'sigstr_landed': 'Avg Significant Strikes Landed', 'ctrl_sec': 'Avg Control (secs)', 'is_winner' : 'Win Ratio',  'sigstr_per_sec': 'Avg Sig Strike Per Sec', 'totstr_per_sec' : 'Avg Total Strike Per Sec', 'count' : 'Count of UFC Fights'})
table_data = table_data.drop(columns = ['win_lose', 'subatt_per_sec'])

df_3.rename(columns= {'tot_fight_secs': 'Fight Time (s)','fighter' : 'Fighter' ,'totstr_landed':'Total Strikes Landed', 'sigstr_landed': 'Significant Strikes Landed', 'ctrl_sec': 'Control Time (s)', 'is_winner' : 'Win Ratio',  'sigstr_per_sec': 'Sig Strike Per Sec', 'totstr_per_sec' : 'Total Strike Per Sec', 'count' : 'Count of UFC Fights'}, inplace=True)

df_2.rename(columns= {'tot_fight_secs': 'Fight Time (s)','fighter' : 'Fighter' ,'totstr_landed':'Total Strikes Landed', 'sigstr_landed': 'Significant Strikes Landed', 'ctrl_sec': 'Control Time (s)', 'is_winner' : 'Win Ratio',  'sigstr_per_sec': 'Sig Strike Per Sec', 'totstr_per_sec' : 'Total Strike Per Sec', 'count' : 'Count of UFC Fights'}, inplace=True)

# Primary win method
wins_method = df[df['is_winner'] == True]
wins_method  = wins_method .groupby(['weight'])[['totstr_landed', 'sigstr_landed', 'ctrl_sec', 'is_winner', 'sigstr_per_sec', 'totstr_per_sec', 'subatt_per_sec']].mean().reset_index()
wins_method.rename(columns= {'tot_fight_secs': 'Fight Time (s)','fighter' : 'Fighter' ,'totstr_landed':'Total Strikes Landed', 'sigstr_landed': 'Significant Strikes Landed', 'ctrl_sec': 'Control Time (s)', 'is_winner' : 'Win Ratio',  'sigstr_per_sec': 'Sig Strike Per Sec', 'totstr_per_sec' : 'Total Strike Per Sec', 'count' : 'Count of UFC Fights'}, inplace=True)
# Primary lose method
lose_method = df[df['is_winner'] == False]
lose_method  = lose_method .groupby(['weight'])[['totstr_landed', 'sigstr_landed', 'ctrl_sec', 'is_winner', 'sigstr_per_sec', 'totstr_per_sec', 'subatt_per_sec']].mean().reset_index()
lose_method.rename(columns= {'tot_fight_secs': 'Fight Time (s)','fighter' : 'Fighter' ,'totstr_landed':'Total Strikes Landed', 'sigstr_landed': 'Significant Strikes Landed', 'ctrl_sec': 'Control Time (s)', 'is_winner' : 'Win Ratio',  'sigstr_per_sec': 'Sig Strike Per Sec', 'totstr_per_sec' : 'Total Strike Per Sec', 'count' : 'Count of UFC Fights'}, inplace=True)

fighter_names = sorted(df['fighter'].unique())

weight_classes = sorted(df['weight'].unique())


# User Interface
app.layout = html.Div(style = {'display':'flex', 'flexDirection':'column'},children=[
    html.Div(style={
        'padding': '10px',
        'textAlign': 'center',
        'backgroundColor': "#e7e7e7",
        'border': '1px solid black',
        'fontFamily': 'Arial, sans-serif'
    }, children = [
    html.H1('UFC Fight Stats - Who Da Buckest', style={'textAlign': 'center'})]),
    
    html.Div(style = {
        'display': 'flex'
    }, children = [
        html.Div(style = {
            'width': '20%',
            'padding' : '5px',
            'border': '1px solid black',
            'fontFamily': 'Arial, sans-serif'
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
            'fontFamily': 'Arial, sans-serif'
        }, children = [
            dcc.Graph(id='avgs-chart'),
            dcc.Graph(id = 'gbar'),
            dash_table.DataTable(
                id = 'fighter-table',
                columns = [{'name': col, 'id': col} for col in table_data.columns],
                data = table_data.to_dict('records'),
                style_table = {'overflowX': 'auto'},
                style_cell = {'textAlign': 'left',
                              'fontFamily': 'Arial, sans-serif',
                              'height' : 'auto',
                              'whiteSpace' : 'normal'},
                style_header = {
                            'backgroundColor' : "#dae3ff",
                            'fontWeight' : 'bold',
                            'textAlign': 'center'
                },
                page_size = 5,
                filter_action= 'native'
            )
        ])])
])

# Callbacks
@app.callback(
    Output('avgs-chart', 'figure'),
    Output('gbar', 'figure'),
    # Input('fighter-name', 'value'),
    Input('weight-class-filter', 'value'),
    Input('fighter-experience', 'value'),
    Input('metric', 'value')
)
def filter_by_weight(selected_wc, fighter_experience, metric):
    
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

    filt_df2 = filt_df2[filt_df2['Count of UFC Fights'] >= fighter_experience]

    filt_df2 = filt_df2.sort_values(by = metric, ascending = False)
    
    # Bar plot development
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x = filt_df2['Fighter'],
        y = filt_df2[metric],
        marker_color = filt_df2['win_lose']
    ))

    fig.update_layout(
        title = f'Average Number of {metric} by Fighter in {bar_title}',
        xaxis_title = 'Fighter',
        yaxis_title = f"Average {metric}",
        xaxis_tickangle = -45
    )
    
    avg_line = round(filt_df2[metric].mean())

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
        xaxis_tickangle = -45
    )
 

    return fig, grouped_bar

if __name__ == '__main__':
    app.run(debug = True)
