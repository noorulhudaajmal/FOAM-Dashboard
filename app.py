import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import streamlit_option_menu as menu
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from utils import Widgets, get_widgets_formats, format_currency_label

st.set_page_config(page_title="F.O.A.M", layout="wide", page_icon="📊")
# ---------------------------------- Page Styling -------------------------------------

with open("css/style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

# ----------------------------------- Data Loading ------------------------------------

active_opportunities = pd.read_csv("ActiveOpportunities.csv")
past_awards = pd.read_csv("PastAwards.csv")

# ------------------------------------ Data pre-processing ----------------------------

active_opportunities["Posted_Date"] = pd.to_datetime(active_opportunities["Posted_Date"])
active_opportunities["Response_Deadline"] = pd.to_datetime(active_opportunities["Response_Deadline"])
active_opportunities["Archive_Date"] = pd.to_datetime(active_opportunities["Archive_Date"])

# ------------------------------------ Menu  -------------------------------------------
with st.sidebar:
    view = menu.option_menu(menu_title="Pages", orientation="vertical", menu_icon=None,
                            options=["Current Opportunities", "Competitor Info", "Forecast Recompetes"])

if view == "Current Opportunities":
    # ------------------------------------ Widgets -----------------------------------------
    st.markdown(get_widgets_formats(Widgets.TITLE).format('#1E3231', 'white', "Current Opportunities"),
                unsafe_allow_html=True)
    # ------------------------------------ Filters ----------------------------------------

    with st.sidebar:
        agency = st.multiselect(label="Agency",
                                options=set(active_opportunities["Awarding_Agency"].values))
        opp_type = st.multiselect(label="Opportunity Type",
                                  options=set(active_opportunities["Type"].values))
        ecs_rating = st.multiselect(label="ECS Rating",
                                    options=set(active_opportunities["Score"].values))
        set_aside_type = st.multiselect(label="Set Aside Type",
                                        options=set(active_opportunities["Set_Aside_Type"].values))
        days_remaining = st.multiselect(label="Days Remaining",
                                        options=set(active_opportunities["DaysRemainingCode"].values))

    # ------------------------------------ Data Filtering ----------------------------------------

    filtered_df = active_opportunities.copy()  # Create a copy of the original DataFrame

    # Check if any filters are selected and apply them
    if agency:
        filtered_df = filtered_df[filtered_df["Awarding_Agency"].isin(agency)]
    if opp_type:
        filtered_df = filtered_df[filtered_df["Type"].isin(opp_type)]
    if ecs_rating:
        filtered_df = filtered_df[filtered_df["Score"].isin(ecs_rating)]
    if set_aside_type:
        filtered_df = filtered_df[filtered_df["Set_Aside_Type"].isin(set_aside_type)]
    if days_remaining:
        filtered_df = filtered_df[filtered_df["DaysRemainingCode"].isin(days_remaining)]

    # ------------------------------------ KPIs ----------------------------------------

    total_opportunities = filtered_df["Notice_ID"].nunique()
    days_to_respond = filtered_df["Days_to_ResponseDeadline"].mean()
    count_positive_ecs = len(filtered_df[filtered_df["Score_Mapped"] == "Positive"])
    count_green = len(filtered_df[filtered_df['DaysRemainingCode'] == 'Green'])

    kpi_row = st.columns(4)

    kpi_row[0].metric(label="Total Opportunities", value=f"{total_opportunities}")
    kpi_row[1].metric(label="Avg. Days to Respond", value=f"{days_to_respond:.1f}")
    kpi_row[2].metric(label="Count of positive ECS Rating", value=f"{count_positive_ecs}")
    kpi_row[3].metric(label="Opportunities with 25+ Days Remaining", value=f"{count_green}")

    # ------------------------------------ Charts ----------------------------------------
    first_chart_row = st.columns(2)
    # ------------------------------------ Opp by Type ----------------------------------------

    opp_by_type = filtered_df.groupby("Type").agg(
        {'Notice_ID': 'count', 'Days_to_ResponseDeadline': 'mean'}
    ).reset_index()
    opp_by_type = opp_by_type.sort_values("Days_to_ResponseDeadline", ascending=True)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=opp_by_type["Type"],
            y=opp_by_type["Notice_ID"],
            name="Number of Opportunities",
            marker_color="#e9c46a"
        )
    )
    fig.add_trace(
        go.Scatter(
            x=opp_by_type["Type"],
            y=opp_by_type["Days_to_ResponseDeadline"],
            mode="lines+markers",
            name="Avg. Days to Respond to Deadline",
            marker_color="#e76f51"
        )
    )
    fig.update_layout(title="OPPORTUNITY BY TYPE", height=400, showlegend=False)

    first_chart_row[0].plotly_chart(fig, use_container_width=True)
    # ------------------------------------ Opp by Agency ----------------------------------------

    opp_by_agency = filtered_df.groupby("Awarding_Agency")["Notice_ID"].count().reset_index()
    opp_by_agency = opp_by_agency.sort_values("Notice_ID", ascending=True)
    opp_by_agency['Awarding_Agency'] = opp_by_agency['Awarding_Agency'].str[
                                       :15]  # Truncate the "Awarding_Agency" column
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=opp_by_agency["Awarding_Agency"],
            x=opp_by_agency["Notice_ID"],
            orientation='h',
            text=opp_by_agency["Notice_ID"],
            marker_color="#8ab17d"
        )
    )
    fig.update_layout(title="OPPORTUNITY BY AWARDING AGENCIES", height=400)

    first_chart_row[1].plotly_chart(fig, use_container_width=True)
    # ------------------------------------ Opp by Posted Month ----------------------------------------

    opp_by_posted_date = filtered_df.groupby("Posted_Date")["Notice_ID"].count().reset_index()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=opp_by_posted_date["Posted_Date"],
                   y=opp_by_posted_date["Notice_ID"],
                   mode="lines+markers+text",
                   text=opp_by_posted_date["Notice_ID"],
                   textposition="top center",
                   fill='tozeroy',
                   fillcolor="#e9c46a",
                   line=dict(color='#e76f51', width=2),
                   marker=dict(color='#e76f51', size=8),
                   name="Opportunity Count")
    )
    fig.update_layout(title="OPPORTUNITY POSTED BY MONTH", height=400)

    first_chart_row[0].plotly_chart(fig, use_container_width=True)

    # ----------------------------------- Avg. Days to Response to Deadline By NAICS --------------------

    avg_days_to_response_NAICS = filtered_df.groupby(
        "NAICSCodeDesc"
    )["Days_to_ResponseDeadline"].mean().reset_index()
    avg_days_to_response_NAICS = avg_days_to_response_NAICS.sort_values("Days_to_ResponseDeadline", ascending=True)
    avg_days_to_response_NAICS['NAICSCodeDesc'] = avg_days_to_response_NAICS['NAICSCodeDesc'].str[:15]
    avg_days_to_response_NAICS = avg_days_to_response_NAICS[:27]
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=avg_days_to_response_NAICS["NAICSCodeDesc"],
            x=avg_days_to_response_NAICS["Days_to_ResponseDeadline"],
            orientation='h',
            text=avg_days_to_response_NAICS["Days_to_ResponseDeadline"],
            marker_color="#8ab17d"
        )
    )
    fig.update_layout(title="AVG. DAYS TO RESPONSE TO DEADLINE BY NAICS", height=400)

    first_chart_row[1].plotly_chart(fig, use_container_width=True)
    # ------------------------------------ Data Chart --------------------------------------

    data = filtered_df.copy()
    fig = go.Figure(data=[go.Table(
        # columnorder=[3, 3, 3, 3, 1, 1,1],
        # columnwidth=[10, 10, 10, 5, 5, 5],
        header=dict(
            values=list(data.columns),
            font=dict(size=24, color='white', family='ubuntu'),
            fill_color='#264653',
            line_color='rgba(255,255,255,0.2)',
            align=['left', 'center'],
            height=100
        ),
        cells=dict(
            values=[data[K].tolist() for K in data.columns],
            font=dict(size=18, color="white", family='ubuntu'),
            align=['left', 'center'],
            fill_color="#a3b18a",
            height=30
        )
    )
    ]
    )
    fig.update_layout(margin=dict(l=0, r=10, b=10, t=30))

    st.plotly_chart(fig, use_container_width=True)

if view == "Competitor Info":
    # ------------------------------------ Widgets -----------------------------------------
    st.markdown(get_widgets_formats(Widgets.TITLE).format('#1E3231', 'white', "Competitor Info"),
                unsafe_allow_html=True)
    # ------------------------------------ Filters ----------------------------------------

    with st.sidebar:
        agency = st.multiselect(label="Agency",
                                options=set(past_awards["Awarding Agency"].values))
        awardee = st.multiselect(label="Awardee",
                                 options=set(past_awards["Recipient Name"].values))
        contract_type = st.multiselect(label="Contract Type",
                                       options=set(past_awards["Contract Award Type"].values))
        contract_status = st.multiselect(label="Contract Status",
                                         options=set(past_awards["Contract Status"].values))
        award_amount_bins = st.multiselect(label="Award Amount Bins",
                                           options=set(past_awards["AwardAmount_Binned"].values))

    # ------------------------------------ Data Filtering ----------------------------------------

    filtered_past_awards = past_awards.copy()  # Create a copy of the original DataFrame

    # Check if any filters are selected and apply them
    if agency:
        filtered_past_awards = filtered_past_awards[filtered_past_awards["Awarding Agency"].isin(agency)]
    if awardee:
        filtered_past_awards = filtered_past_awards[filtered_past_awards["Recipient Name"].isin(awardee)]
    if contract_type:
        filtered_past_awards = filtered_past_awards[filtered_past_awards["Contract Award Type"].isin(contract_type)]
    if contract_status:
        filtered_past_awards = filtered_past_awards[filtered_past_awards["Contract Status"].isin(contract_status)]
    if award_amount_bins:
        filtered_past_awards = filtered_past_awards[filtered_past_awards["AwardAmount_Binned"].isin(award_amount_bins)]

    # ------------------------------------ KPIs ----------------------------------------

    total_past_awards = filtered_past_awards["generated_internal_id"].nunique()
    six_million_above = len(filtered_past_awards[
                                (filtered_past_awards["AwardAmount_Binned"] == "6-12 million") |
                                (filtered_past_awards["AwardAmount_Binned"] == "12+ million")])
    award_amount = filtered_past_awards["Award Amount"].sum()

    kpi_row = st.columns(3)

    kpi_row[0].metric(label="Total Number of Past Awards", value=f"{total_past_awards}")
    kpi_row[1].metric(label="Number of Awards Value $6+ Million", value=f"{six_million_above}")
    kpi_row[2].metric(label="Total Past Award(s) Amount", value=f"${format_currency_label(award_amount)}")

    # ------------------------------------ Charts ----------------------------------------
    first_chart_row = st.columns(2)
    # ------------------------------------ Number of Awards By Recipient -----------------

    awards_by_recipient = filtered_past_awards.groupby("Recipient Name")["generated_internal_id"].count().reset_index()
    awards_by_recipient = awards_by_recipient.sort_values("generated_internal_id", ascending=True)
    awards_by_recipient.rename(columns={"generated_internal_id": "Number of Awards"}, inplace=True)
    awards_by_recipient = awards_by_recipient[:10]

    fig = px.pie(awards_by_recipient, values='Number of Awards', names='Recipient Name',
                 hole=0.3, title="NUMBER OF PAST AWARDS BY RECIPIENTS", height=500,
                 labels={'Recipient Name': 'Recipient Name'})
    fig.update_traces(textinfo='percent+value')

    first_chart_row[0].plotly_chart(fig, use_container_width=True)
    # ------------------------------------ Amount of Awards By Recipient ----------------------------------------

    awards_amount_by_recipient = filtered_past_awards.groupby("Recipient Name")["Award Amount"].sum().reset_index()
    awards_amount_by_recipient['Formatted Award Amount'] = awards_amount_by_recipient['Award Amount'].apply(
        format_currency_label)
    awards_amount_by_recipient = awards_amount_by_recipient[:10]

    fig = px.pie(awards_amount_by_recipient, values='Award Amount', names='Recipient Name',
                 hole=0.3, title="PAST AWARDS AMOUNT BY RECIPIENTS", height=500,
                 labels={'Recipient Name': 'Recipient Name'})
    fig.update_traces(textinfo='percent')

    first_chart_row[1].plotly_chart(fig, use_container_width=True)
    # ------------------------------------ Award Amount Chart ----------------------------------------

    award_amount_df = filtered_past_awards.groupby("Awarding Agency").agg(
        {'Award ID': 'count', 'Award Amount': 'sum'}
    ).reset_index()
    award_amount_df['Award Amount'] = award_amount_df['Award Amount'].apply(
        format_currency_label)
    award_amount_df.rename(columns={"Award ID": "Number of Awards"}, inplace=True)

    fig = go.Figure(data=[go.Table(
        columnwidth=[10, 5, 10],
        header=dict(
            values=list(award_amount_df.columns),
            font=dict(size=24, color='white', family='ubuntu'),
            fill_color='#264653',
            line_color='rgba(255,255,255,0.2)',
            align=['left', 'center'],
            height=100
        ),
        cells=dict(
            values=[award_amount_df[K].tolist() for K in award_amount_df.columns],
            font=dict(size=18, color="white", family='ubuntu'),
            align=['left', 'center'],
            fill_color="#74a57f",
            height=30
        )
    )
    ]
    )
    fig.update_layout(margin=dict(l=0, r=10, b=10, t=30), title="PAST AWARDS AMOUNT BY AWARDING AGENCY")

    first_chart_row[0].plotly_chart(fig, use_container_width=True)

    # ------------------------------------ Award Amount Chart#2 ----------------------------------------
    award_amount_by_recp_naics_df = filtered_past_awards.groupby(
        ["naics_description", "Awarding Agency"]
    )['Award Amount'].sum().reset_index()
    award_amount_by_recp_naics_df = award_amount_by_recp_naics_df.sort_values(by="Award Amount", ascending=False)
    award_amount_by_recp_naics_df['Award Amount'] = award_amount_by_recp_naics_df['Award Amount'].apply(
        format_currency_label)
    award_amount_by_recp_naics_df.rename(columns={"naics_description": "NAICS"}, inplace=True)

    fig = go.Figure(data=[go.Table(
        columnwidth=[10, 10, 5],
        header=dict(
            values=list(award_amount_by_recp_naics_df.columns),
            font=dict(size=24, color='white', family='ubuntu'),
            fill_color='#264653',
            line_color='rgba(255,255,255,0.2)',
            align=['left', 'center'],
            height=100
        ),
        cells=dict(
            values=[award_amount_by_recp_naics_df[K].tolist() for K in award_amount_by_recp_naics_df.columns],
            font=dict(size=18, color="white", family='ubuntu'),
            align=['left', 'center'],
            fill_color="#74a57f",
            height=30
        )
    )
    ]
    )
    fig.update_layout(margin=dict(l=0, r=10, b=10, t=30), title="PAST AWARDS AMOUNT BY NAICS AND RECIPIENT")

    first_chart_row[1].plotly_chart(fig, use_container_width=True)
    # # ----------------------------------- Avg. Days to Response to Deadline By NAICS --------------------
    #
    # avg_days_to_response_NAICS = filtered_df.groupby(
    #     "NAICSCodeDesc"
    # )["Days_to_ResponseDeadline"].mean().reset_index()
    # avg_days_to_response_NAICS = avg_days_to_response_NAICS.sort_values("Days_to_ResponseDeadline", ascending=True)
    # avg_days_to_response_NAICS['NAICSCodeDesc'] = avg_days_to_response_NAICS['NAICSCodeDesc'].str[:15]
    # avg_days_to_response_NAICS = avg_days_to_response_NAICS[:27]
    # fig = go.Figure()
    # fig.add_trace(
    #     go.Bar(
    #         y=avg_days_to_response_NAICS["NAICSCodeDesc"],
    #         x=avg_days_to_response_NAICS["Days_to_ResponseDeadline"],
    #         orientation='h',
    #         text=avg_days_to_response_NAICS["Days_to_ResponseDeadline"],
    #         marker_color="#8ab17d"
    #     )
    # )
    # fig.update_layout(title="AVG. DAYS TO RESPONSE TO DEADLINE BY NAICS", height=400)
    #
    # first_chart_row[1].plotly_chart(fig, use_container_width=True)

if view == "Forecast Recompetes":
    # ------------------------------------ Widgets -----------------------------------------
    st.markdown(get_widgets_formats(Widgets.TITLE).format('#1E3231', 'white', "Forecast Recompetes"),
                unsafe_allow_html=True)
    # ------------------------------------ Filters ----------------------------------------

    with st.sidebar:
        agency = st.multiselect(label="Agency",
                                options=set(past_awards["Awarding Agency"].values))
        incumbent = st.multiselect(label="Incumbent Name",
                                   options=set(past_awards["Recipient Name"].values))
        contract_status = st.multiselect(label="Contract Status",
                                         options=set(past_awards["Contract Status"].values))
        months_to_end = st.multiselect(label="Months To Contracts Ends",
                                       options=set(past_awards["Months Until Contract Ends"].values))

    # ------------------------------------ Data Filtering ----------------------------------------

    filtered_contracts_data = past_awards.copy()  # Create a copy of the original DataFrame

    # Check if any filters are selected and apply them
    if agency:
        filtered_contracts_data = filtered_contracts_data[
            filtered_contracts_data["Awarding Agency"].isin(agency)]
    if incumbent:
        filtered_contracts_data = filtered_contracts_data[
            filtered_contracts_data["Recipient Name"].isin(incumbent)]
    if contract_status:
        filtered_contracts_data = filtered_contracts_data[
            filtered_contracts_data["Contract Award Type"].isin(contract_status)]
    if months_to_end:
        filtered_contracts_data = filtered_contracts_data[
            filtered_contracts_data["Contract Status"].isin(months_to_end)]
    # ------------------------------------ KPIs ----------------------------------------

    contracts_count = filtered_contracts_data["generated_internal_id"].nunique()
    total_offers = filtered_contracts_data['number_of_offers_received'].sum()
    filtered_records = filtered_contracts_data[
        (filtered_contracts_data['number_of_offers_received'] > 0)
        | (filtered_contracts_data['number_of_offers_received'].notna())
        ]
    num_unique_contracts = len(filtered_records['generated_internal_id'].unique())
    if num_unique_contracts == 0:
        average_offers_per_contract = 0
    else:
        average_offers_per_contract = total_offers / num_unique_contracts
    contracts_value = filtered_contracts_data["Award Amount"].sum()

    kpi_row = st.columns(3)

    kpi_row[0].metric(label="Count of Contracts", value=f"{contracts_count}")
    kpi_row[1].metric(label="Avg. Offers Per Contract", value=f"{average_offers_per_contract:.2f}")
    kpi_row[2].metric(label="Contract(s) Value", value=f"${format_currency_label(contracts_value)}")

    # ------------------------------------ Charts ----------------------------------------
    first_chart_row = st.columns(2)

    # --------------------- Frequent words in past awards description --------------------
    description_text = " ".join(filtered_contracts_data["Description"].dropna())

    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(description_text)
    fig = px.imshow(wordcloud, binary_string=True)
    fig.update_layout(title="FREQUENT WORDS IN PAST AWARDS DESCRIPTION")
    first_chart_row[0].plotly_chart(fig, use_container_width=True)

    # --------------------- Award Amount By Months Until Contract Ends -------------------

    award_amount_by_months = filtered_contracts_data.groupby(
        ["Months Until Contract Ends", "Recipient Name"]
    )["Award Amount"].sum().reset_index()
    award_amount_by_months["Symbol"] = "diamond"
    award_amount_by_months = award_amount_by_months[
        award_amount_by_months["Months Until Contract Ends"] != "Contract/s Expired"
        ]
    fig = px.scatter(data_frame=award_amount_by_months, x="Months Until Contract Ends",
                     y="Award Amount",
                     color="Recipient Name",
                     symbol_sequence=list(award_amount_by_months["Symbol"].values),
                     title="AWARD AMOUNT BY MONTHS UNTIL CONTRACT ENDS",
                     )

    first_chart_row[0].plotly_chart(fig, use_container_width=True)
    # --------------------- Award Amount By Contract Duration (Years) -------------------

    award_amount_by_duration = filtered_contracts_data.groupby(
        ["Contract Duration (Years)", "Recipient Name"]
    )["Award Amount"].sum().reset_index()
    award_amount_by_duration["Symbol"] = "diamond"

    fig = px.bar(data_frame=award_amount_by_duration,
                 x="Contract Duration (Years)",
                 y="Award Amount",
                 color="Recipient Name",
                 title="AWARD AMOUNT BY CONTRACT DURATION (Years)",
                 height=800
                 )

    first_chart_row[1].plotly_chart(fig, use_container_width=True)
    # ------------------------------------ Filtered dataframe ----------------------------
    st.dataframe(filtered_contracts_data, use_container_width=True)