import pandas as pd

from dash import Dash, html, dcc, Input, Output
import plotly.express as px


def get_data_by_filters(genres, ratings, years):
    genres = list(genres) if type(genres) == str else genres
    ratings = list(ratings) if type(ratings) == str else ratings
    
    filtered_df = df_cleaned[(df_cleaned['Genre'].isin(genres)) 
                             & (df_cleaned['Year_of_Release'].between(years[0], years[1]))
                             & (df_cleaned['Rating'].isin(ratings))]
    return filtered_df


data_path = '.'

df = pd.read_csv(f'{data_path}/games.csv')
df = df[df['User_Score'] != 'tbd']
df['User_Score'] = df['User_Score'].astype('float')

df_cleaned = df[df['Year_of_Release'] >= 2000].dropna().copy()
df_cleaned['Year_of_Release'] = df_cleaned['Year_of_Release'].astype('int')

actual_genres = df_cleaned['Genre'].unique()
actual_ratings = df_cleaned['Rating'].unique()
actual_years = df_cleaned['Year_of_Release'].unique()

app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Дашборд состояния игровой индустрии', style={'text-align': 'center', 'padding': 10, 'backgroundColor': 'rgba(217, 95, 2, 50%)'}),
    
    html.H4(children='''
            На дашборде показана основная информация
            об играх за 2000-2016 года. В данных присутствуют игры для различных платформ, 
            разного рейтинга и жанров. С помощью интерактивного дашборда можно
            провести аналитику по популярности игр в зависимости от года выпуска, жанра и т.д.
            ''', style={'padding-left': '10%', 'padding-right': '10%'}),
    
    html.H4(children='''
            Как пользоваться:
            Задайте в фильтрах значения жанра, рейтинга и года. 
            Введенные значения будут использованы в графиках.
            '''
            , style={'padding-left': '10%', 'padding-right': '10%'}),
    
    html.Div(children=[
        html.Div(children=[
            html.Label('Фильтр жанров:'),
            dcc.Dropdown(actual_genres
                         , multi=True
                         , id='filter-genres'
                         , value=['Action', 'Sports', 'Racing']
                         , style={'color': 'rgb(102, 102, 102)'}),
        ], style={'width': '45%', 'display': 'inline-block', 'float': 'left'}),
    
        html.Div(children=[
            html.Label('Фильтр рейтингов:'),
            dcc.Dropdown(actual_ratings
                         , multi=True
                         , id='filter-ratings'
                         , value=['E']
                         , style={'color': 'rgb(102, 102, 102)'})
        ], style={'width': '45%', 'display': 'inline-block', 'float': 'right'}),
    ], style={'padding': 10}),
    
    
    html.Div(children=[
        html.H4(children=[], id='games-count')
    ], style={'width': '100%', 'display': 'inline-block', 'margin': 10, 'backgroundColor': 'rgba(217, 95, 2, 50%)', 'text-align': 'center'}),
    
    
    html.Div(children=[
        html.Div(children=[
            dcc.Graph(id='graph-area')
        ], style={'width': '50%', 'display': 'inline-block', 'float': 'left'}),
        
        html.Div(children=[
            dcc.Graph(id='graph-scatter')
        ], style={'width': '50%', 'display': 'inline-block', 'float': 'right'})
    ], style={'width': '100%', 'display': 'inline-block'}),


    html.Div(children=[
        html.Label('Интервал годов выпуска:'),
        dcc.RangeSlider(
            min=min(actual_years)
            , max=max(actual_years)
            , step=1
            , value=[2002, 2010]
            , marks={str(year): str(year) for year in actual_years}
            , id='filter-years')
    ], style={'width': '100%', 'display': 'inline-block', 'padding': 10, 'text-align': 'center'})
], style={'width': '100%'})


@app.callback(
    Output("graph-scatter", "figure"), 
    Input("filter-genres", "value"),
    Input("filter-years", "value"),
    Input("filter-ratings", "value")
    )
def update_scatter_plot(genres, years, ratings):
    df = get_data_by_filters(genres, ratings, years)
    fig = px.scatter(df
                     , x='User_Score'
                     , y='Critic_Score'
                     , color='Genre'
                     , title='Оценки игр по жанрам'
                     , labels={'User_Score': 'Оценка игроков'
                               , 'Critic_Score': 'Оценка критиков'
                               , 'Genre': 'Жанр'}
                     , color_discrete_sequence=px.colors.qualitative.Dark2)
    fig.update_layout({'title_font_color': 'rgb(217, 95, 2)'})
    return fig


@app.callback(
    Output("graph-area", "figure"), 
    Input("filter-genres", "value"),
    Input("filter-years", "value"),
    Input("filter-ratings", "value")
    )
def update_area_plot(genres, years, ratings):
    df = get_data_by_filters(genres, ratings, years)
    df_grouped = df.groupby(['Year_of_Release', 'Platform']).agg('count').reset_index()
    fig = px.area(df_grouped
                  , x='Year_of_Release'
                  , y='Name'
                  , color='Platform'
                  , title='Выпуск игр по годам и платформам'
                  , labels={'Year_of_Release': 'Год выпуска'
                            , 'Name': 'Количество игр'
                            , 'Platform': 'Платформа'}
                  , color_discrete_sequence=px.colors.qualitative.Dark2)
    fig.update_layout({'title_font_color': 'rgb(217, 95, 2)'})
    return fig


@app.callback(
    Output("games-count", "children"), 
    Input("filter-genres", "value"),
    Input("filter-years", "value"),
    Input("filter-ratings", "value")
    )
def update_games_count(genres, years, ratings):
    return f'Количество выбранных игр: {get_data_by_filters(genres, ratings, years).shape[0]}'


if __name__ == '__main__':
    app.run_server(debug=True)
