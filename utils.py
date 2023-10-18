from enum import Enum
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import streamlit_option_menu as menu
from wordcloud import WordCloud


class Widgets(Enum):
    TITLE = 1
    SUB_TITLE = 2
    HEAD_TITLE = 3
    COLORS = 5


def get_widgets_formats(widget_type: Widgets):
    match widget_type:
        case Widgets.TITLE:
            return """
                <div style="background-color:{};padding:10px;border-radius:10px">
                <h1 style="color:{};text-align:center;">{}</h1>
                </div>
                """
        case Widgets.SUB_TITLE:
            return """
                <div style="background-color:{};padding:0.5px;border-radius:5px;">
                <h4 style="color:{};text-align:center;">{}</h6>
                </div>
                """
        case Widgets.HEAD_TITLE:
            return """<h6 style="text-align:left;margin-top:2px">{}</h6>"""

        case Widgets.COLORS:
            return ["#2a9d8f", "#74a57f", "#8ab17d", "#8bb174", "#e9c46a", "#efb366", "#f4a261", "#ee8959",
                    "#e76f51", "#e76f51", "#e76f51", "#e76f51", "#e76f51", "#e76f51", "#e76f51", "#e76f51",
                    "#e76f51", "#e76f51", "#e76f51", "#e76f51", "#e76f51", "#e76f51", "#e76f51", "#e76f51",
                    "#e76f51", "#e76f51", "#e76f51", "#e76f51"]


def pre_process_data(data: pd.DataFrame):
    data["Posted_Date"] = pd.to_datetime(data["Posted_Date"])
    # data["Response_Deadline"] = pd.to_datetime(data["Response_Deadline"])
    data["DaysRemainingCode"] = data["DaysRemainingCode"].map({
        "Red": "#e76f51",
        "Yellow": "#e9c46a",
        "Green": "#52b788"
    })

    return data


def opportunities_table(data: pd.DataFrame, columns: list):
    table_data = data[columns]
    table_data.rename(columns={
        "Awarding_Agency": "Awarding Agency",
        "Days_to_ResponseDeadline": "Days Remaining",
        "Description link": "URL",
        "NAICSCodeDesc": "NAICS",
        "Set_Aside_Type": "Set Aside",
        "Score": "ECS Rating",
        "Posted_Date": "Posted Date"
    }, inplace=True)
    table_data["Posted Date"] = table_data["Posted Date"].dt.date

    fig = go.Figure(data=[go.Table(
        columnwidth=[2, 2, 2, 1, 1, 4, 2, 1, 1],
        header=dict(
            values=list(table_data.columns),
            font=dict(size=18, color='white', family='ubuntu'),
            fill_color='#264653',
            align=['left', 'center'],
            height=80
        ),
        cells=dict(
            values=[table_data[K].tolist() for K in table_data.columns],
            font=dict(size=12, color="black", family='ubuntu'),
            fill_color=['#f5ebe0', '#f5ebe0', '#f5ebe0', '#f5ebe0',
                        data["DaysRemainingCode"].values, '#f5ebe0'],
            height=80
        )
    )
    ]
    )
    fig.update_layout(margin=dict(l=0, r=10, b=10, t=30), height=500)
    return fig


def current_opportunities_kpis(data: pd.DataFrame):
    total_opportunities = data["Notice_ID"].nunique()
    days_to_respond = data["Days_to_ResponseDeadline"].mean()
    count_positive_ecs = len(data[data["Score_Mapped"] == "Positive"])
    count_green = len(data[data['DaysRemainingCode'] == 'Green'])

    return total_opportunities, days_to_respond, count_positive_ecs, count_green


def competitor_kpis(data: pd.DataFrame):
    total_past_awards = data["generated_internal_id"].nunique()
    six_million_above = len(data[
                                (data["AwardAmount_Binned"] == "6-12 million") |
                                (data["AwardAmount_Binned"] == "12+ million")])
    award_amount = data["Award Amount"].sum()
    return total_past_awards, six_million_above, award_amount


def bar_scatter_chart(data: pd.DataFrame, bar_X: str, bar_Y: str, bar_name: str,
                      scatter_X: str, scatter_Y: str, scatter_name, title):
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=data[bar_X],
            y=data[bar_Y],
            name=bar_name,
            marker_color="#00b4d8"
        )
    )
    fig.add_trace(
        go.Scatter(
            x=data[scatter_X],
            y=data[scatter_Y],
            mode="lines+markers",
            name=scatter_name,
            marker_color="#ff4d6d"
        )
    )
    fig.update_layout(title=title, height=400, showlegend=False,
                      hovermode="x unified",
                      hoverlabel=dict(
                          bgcolor="white",
                          font_color="black",
                          font_size=16,
                          font_family="Rockwell"
                      ))
    return fig


def bar_chart(data: pd.DataFrame, x: str, y: str, orient: str, title: str, text=None, pre_hover_text=None):
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=data[y],
            x=data[x],
            orientation=orient,
            text=data[text],
            marker_color="#00b4d8",
            hovertext=pre_hover_text + " " + (round(data[text], 2)).astype(str)
        )
    )
    fig.update_layout(title=title, height=400,
                      hovermode="x unified",
                      hoverlabel=dict(
                          bgcolor="white",
                          font_color="black",
                          font_size=16,
                          font_family="Rockwell"
                      ))
    return fig


def scatter_plot(data: pd.DataFrame, x: str, y: str, title: str, name, text=None):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=data[x],
                   y=data[y],
                   mode="lines+markers+text",
                   text=data[text],
                   textposition="top center",
                   fill='tozeroy',
                   fillcolor="#90e0ef",
                   line=dict(color='#e63946', width=2),
                   marker=dict(color='#e63946', size=8),
                   name=name,
                   hovertext=str(name) + " " + data[text].astype(str)
                   )
    )
    fig.update_layout(title=title, height=400,
                      hovermode="x unified",
                      hoverlabel=dict(
                          bgcolor="white",
                          font_color="black",
                          font_size=16,
                          font_family="Rockwell"
                      ))
    return fig


def pie_chart(data: pd.DataFrame, values: str, names: str, title: str, text_info: str):
    fig = px.pie(data, values=values, names=names,
                 hole=0.3, title=title, height=500)
    fig.update_traces(textinfo=text_info,
                      hoverlabel=dict(
                          bgcolor="white",
                          font_color="black",
                          font_size=16,
                          font_family="Rockwell"
                      )
                      )
    return fig


def awards_table(data: pd.DataFrame, columns: list):
    table_data = data[columns]
    table_data.rename(columns={
        "AwardAmount_Binned": "Award Size",
        "PastAwards_URL": "URL"
    }, inplace=True)
    table_data["Award Amount"] = table_data["Award Amount"].apply(format_currency_label)
    fig = go.Figure(data=[go.Table(
        columnwidth=[1, 1, 1, 1, 1, 1, 1, 1, 1, 5],
        header=dict(
            values=list(table_data.columns),
            font=dict(size=18, color='white', family='ubuntu'),
            fill_color='#264653',
            align=['left', 'center'],
            height=80
        ),
        cells=dict(
            values=[table_data[K].tolist() for K in table_data.columns],
            font=dict(size=12, color="black", family='ubuntu'),
            fill_color='#f5ebe0',
            height=80
        ))]
    )
    fig.update_layout(margin=dict(l=0, r=10, b=10, t=30), height=500)
    return fig


def table_chart(data: pd.DataFrame, title: str):
    fig = go.Figure(data=[go.Table(
        columnwidth=[1, 1, 1],
        header=dict(
            values=list(data.columns),
            font=dict(size=18, color='white', family='ubuntu'),
            fill_color='#264653',
            align=['left', 'center'],
            height=80
        ),
        cells=dict(
            values=[data[K].tolist() for K in data.columns],
            font=dict(size=12, color="black", family='ubuntu'),
            fill_color='#f5ebe0',
            height=50
        ))]
    )
    fig.update_layout(margin=dict(l=0, r=10, b=10, t=30), height=500,
                      title=title)
    return fig


def contracts_kpis(data: pd.DataFrame):
    contracts_count = data["generated_internal_id"].nunique()
    total_offers = data['number_of_offers_received'].sum()
    filtered_records = data[
        (data['number_of_offers_received'] > 0)
        | (data['number_of_offers_received'].notna())
        ]
    num_unique_contracts = len(filtered_records['generated_internal_id'].unique())
    if num_unique_contracts == 0:
        average_offers_per_contract = 0
    else:
        average_offers_per_contract = total_offers / num_unique_contracts
    contracts_value = data["Award Amount"].sum()

    return contracts_count, average_offers_per_contract, contracts_value


def forecast_table(data: pd.DataFrame, columns: list):
    table_data = data[columns]
    table_data.rename(columns={
        "Recipient Name": "Incumbent Name",
        "naics_description": "Description",
        "Award Amount": "Current Award Amount",
        "PastAwards_URL": "URL"
    }, inplace=True)
    table_data["Current Award Amount"] = table_data["Current Award Amount"].apply(format_currency_label)
    fig = go.Figure(data=[go.Table(
        columnwidth=[1, 1, 1, 2, 1, 1, 1, 1, 1, 5],
        header=dict(
            values=list(table_data.columns),
            font=dict(size=18, color='white', family='ubuntu'),
            fill_color='#264653',
            align=['left', 'center'],
            height=80
        ),
        cells=dict(
            values=[table_data[K].tolist() for K in table_data.columns],
            font=dict(size=12, color="black", family='ubuntu'),
            fill_color='#f5ebe0',
            height=80
        ))]
    )
    fig.update_layout(margin=dict(l=0, r=10, b=10, t=30), height=500)
    return fig


def format_currency_label(value):
    if value >= 1e9:  # Billion
        return f'{value / 1e9:.2f} bn'
    elif value >= 1e6:  # Million
        return f'{value / 1e6:.2f} M'
    elif value >= 1e3:  # Thousand
        return f'{value / 1e3:.2f} K'
    else:
        return f'{value:.2f}'
