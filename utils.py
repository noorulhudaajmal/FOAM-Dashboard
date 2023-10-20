import datetime

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

power_bi_colors = [
    "#3f37c9",  # Blue
    "#FF6C00",  # Orange
    "#007f5f",
    "#7B00B4",  # Purple
    "#FF0000",  # Red
    "#6A007F",  # Dark Purple
    "#fdd85d",  # Yellow
    "#0077b6",  # Light Blue
    "#aacc00",  # Green
    "#495057",  # Gray
]

metric_div_1 = """
    <div data-testid="metric-container" style="background:#708d81;
    border-radius:10px;text-align:center;margin:8px;width:80%;margin-left:30px;">
      <label data-testid="stMetricLabel" visibility="0" class="css-q49buc e1i5pmia2">
        <div class="css-1wivap2 e1i5pmia3">
          <div data-testid="stMarkdownContainer" class="css-q8sbsg e1nzilvr5">
            <h4 style="color:white;">{label}</h4>
          </div>
        </div>
      </label>
      <div data-testid="stMetricValue" class="css-1xarl3l e1i5pmia1">
        <div class="css-1wivap2 e1i5pmia3">{value}</div>
      </div>
    </div>
"""

metric_div = """
    <div data-testid="metric-container" style="background:#708d81;
    border-radius:10px;text-align:center;">
      <label data-testid="stMetricLabel" visibility="0" class="css-q49buc e1i5pmia2">
        <div class="css-1wivap2 e1i5pmia3">
          <div data-testid="stMarkdownContainer" class="css-q8sbsg e1nzilvr5">
            <h4 style="color:white; text-align:center;">{label}</h4>
          </div>
        </div>
      </label>
      <div data-testid="stMetricValue" class="css-1xarl3l e1i5pmia1">
        <div class="css-1wivap2 e1i5pmia3">{value}</div>
      </div>
    </div>
"""


def kpi_widget(label, value):
    return metric_div.format(label=label, value=value)


def pre_process_data(data: pd.DataFrame):
    data["DaysRemainingColor"] = data["DaysRemainingCode"].map({
        "Red": "#e76f51",
        "Yellow": "#e9c46a",
        "Green": "#52b788"
    })
    return data


def opportunities_table(data: pd.DataFrame, columns: list):
    data = format_date_column(data)
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
    table_data["URL"] = table_data["URL"].apply(lambda x: f"""<a href="{x}">Visit</a>""")
    fig = go.Figure(data=[go.Table(
        columnwidth=[2, 2, 2, 1, 1, 1, 2, 1, 1],
        header=dict(
            values=list(table_data.columns),
            font=dict(size=14, color='white', family='ubuntu'),
            fill_color='#264653',
            align=['center'],
            height=80
        ),
        cells=dict(
            values=[table_data[K].tolist() for K in table_data.columns],
            font=dict(size=12, color="black", family='ubuntu'),
            fill_color=['#f5ebe0', '#f5ebe0', '#f5ebe0', '#f5ebe0',
                        data["DaysRemainingColor"].values, '#f5ebe0'],
            align=['center'],
            height=80
        ))]
    )
    fig.update_layout(margin=dict(l=0, r=10, b=10, t=30), height=500)
    return fig


def forecast_table(data: pd.DataFrame, columns: list):
    data = format_date_column(data)
    table_data = data[columns]
    table_data.rename(columns={
        "Recipient Name": "Incumbent Name",
        "naics_description": "Description",
        "Award Amount": "Current Award Amount",
        "PastAwards_URL": "URL"
    }, inplace=True)
    table_data["Current Award Amount"] = table_data["Current Award Amount"].apply(format_currency_label)
    table_data["URL"] = table_data["URL"].apply(lambda x: f"""<a href="{x}">Visit</a>""")
    fig = go.Figure(data=[go.Table(
        columnwidth=[1, 1, 1, 2, 1, 1, 1, 1, 1, 1],
        header=dict(
            values=list(table_data.columns),
            font=dict(size=14, color='white', family='ubuntu'),
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


def awards_table(data: pd.DataFrame, columns: list):
    data = format_date_column(data)
    table_data = data[columns]
    table_data.rename(columns={
        "AwardAmount_Binned": "Award Size",
        "PastAwards_URL": "URL"
    }, inplace=True)
    table_data["Award Amount"] = table_data["Award Amount"].apply(format_currency_label)
    table_data["URL"] = table_data["URL"].apply(lambda x: f"""<a href="{x}">Visit</a>""")
    fig = go.Figure(data=[go.Table(
        columnwidth=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        header=dict(
            values=list(table_data.columns),
            font=dict(size=14, color='white', family='ubuntu'),
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


def current_opportunities_kpis(data: pd.DataFrame):
    total_opportunities = data["Notice_ID"].nunique()
    days_to_respond = data["Days_to_ResponseDeadline"].mean()
    count_positive_ecs = len(data[data["Score_Mapped"] == "Positive"])
    count_green = len(data[data['DaysRemainingCode'] == "Green"])

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
            marker_color="#094780",
            text=data[bar_Y]
        )
    )
    fig.add_trace(
        go.Scatter(
            x=data[scatter_X],
            y=data[scatter_Y],
            mode="lines+markers+text",
            name=scatter_name,
            line=dict(color='#ff4d6d', width=4),
            marker=dict(color='#ff4d6d', size=10),
            text=round(data[scatter_Y],1),
            textposition="top left",
            textfont=dict(color='#ff4d6d', size=18)
        )
    )
    fig.update_layout(title=title, height=600, showlegend=False, xaxis_title=bar_X, yaxis_title="Count",
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
            x=data[x].astype(int),
            orientation=orient,
            text=data[text].astype(int),
            marker_color="#094780",
            hovertext=pre_hover_text + " " + (round(data[text], 2)).astype(str),
        )
    )
    fig.update_layout(title=title, height=600,
                      hovermode="x unified",
                      hoverlabel=dict(
                          bgcolor="white",
                          font_color="black",
                          font_size=16,
                          font_family="Rockwell"
                      ), yaxis=dict(tickfont=dict(size=20))
                      )
    return fig


def binned_bar_chart(data: pd.DataFrame, x: str, y: str, color: str, title):
    data = data[(data[x] <= 10) & (data[x] >= 1)]
    data[color] = data[color].str[:20]
    fig = px.bar(data_frame=data,
                 x=x,
                 y=y,
                 color=color,
                 title=title,
                 color_discrete_sequence=["#f1ba0a", "#a70b0b", "#03045e", "#4cc9f0",
                                          "#495057", "#012a4a", "#ff0a54", "#aacc00",
                                          "#0096c7", "#2d6a4f", "#7209b7"]
                 )
    fig.update_layout(title=title, height=500)
    return fig


def binned_scatter_plot(data: pd.DataFrame, x: str, y: str, color: str, title: str):
    data[color] = data[color].str[:20]
    fig = px.scatter(data_frame=data, x=x,
                     y=y,
                     color=color,
                     symbol_sequence=list(["diamond"] * len(data)),
                     title=title,
                     color_discrete_sequence=["#f1ba0a", "#a70b0b", "#03045e", "#4cc9f0",
                                              "#495057", "#012a4a", "#ff0a54", "#aacc00",
                                              "#0096c7", "#2d6a4f", "#7209b7"]
                     )
    fig.update_layout(title=title, height=500)
    fig.update_xaxes(categoryorder='array', categoryarray=['0-3 months', '3-6 months',
                                                           '6-12 months', '12-18 months',
                                                           '18+ months'])
    fig.update_traces(marker={'size': 15})
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
                   fillcolor="#00b4d8",
                   line=dict(color='#094780', width=2),
                   marker=dict(color='#094780', size=8),
                   name=name,
                   hovertext=str(name) + " " + data[text].astype(str)
                   )
    )
    fig.update_layout(title=title, height=600, xaxis_title="Posted Date", yaxis_title="Count",
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
                 hole=0.3, title=title, height=500, color_discrete_sequence=power_bi_colors[::-1])
    fig.update_traces(textinfo=text_info,
                      hoverlabel=dict(
                          bgcolor="white",
                          font_color="black",
                          font_size=16,
                          font_family="Rockwell"
                      )
                      )
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
            fill_color='#f0efeb',
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


def format_currency_label(value):
    if value >= 1e9:  # Billion
        return f'{value / 1e9:.2f} bn'
    elif value >= 1e6:  # Million
        return f'{value / 1e6:.2f} M'
    elif value >= 1e3:  # Thousand
        return f'{value / 1e3:.2f} K'
    else:
        return f'{value:.2f}'


def format_date_column(data):
    if len(data) != 0:
        for i in data.columns:
            if isinstance(data[i].iloc[0], datetime.datetime):
                data[i] = data[i].dt.strftime("%m-%d-%Y")
    return data
