import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import streamlit_option_menu as menu
from wordcloud import WordCloud
from utils import Widgets, get_widgets_formats, format_currency_label, \
    current_opportunities_kpis, bar_scatter_chart, bar_chart, scatter_plot, pre_process_data, opportunities_table, \
    competitor_kpis, pie_chart, awards_table, table_chart, contracts_kpis, forecast_table, binned_bar_chart, \
    binned_scatter_plot

st.set_page_config(page_title="F.O.A.M", layout="wide", page_icon="📊")
# ---------------------------------- Page Styling -------------------------------------

with open("css/style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

st.markdown("""
<style>
    [data-testid=stSidebar] {
        background-color: #708d81;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image('./assets/icon.png')

# ----------------------------------- Data Loading ------------------------------------

active_opportunities = pd.read_csv("ActiveOpportunities.csv",
                                   usecols=["Awarding_Agency", "Title", "DescriptionText", "Type",
                                            "Score", "Set_Aside_Type",
                                            "DaysRemainingCode", "Notice_ID", "Score_Mapped",
                                            "Days_to_ResponseDeadline", "Posted_Date",
                                            "NAICSCodeDesc", "Description link"
                                            ])
past_awards = pd.read_csv("PastAwards.csv",
                          usecols=["Award ID", "Awarding Agency", "Recipient Name",
                                   "Contract Award Type", "Contract Status", "naics_description",
                                   "AwardAmount_Binned", "generated_internal_id", "Award Amount",
                                   "Description", "Start Date", "End Date", "Last Modified Date",
                                   "Months Until Contract Ends", "PastAwards_URL",
                                   "number_of_offers_received", "Contract Duration (Years)"])

# ------------------------------------ Data pre-processing ----------------------------
active_opportunities = pre_process_data(active_opportunities)
# ------------------------------------ Menu  -------------------------------------------
view = menu.option_menu(menu_title=None, orientation="horizontal", menu_icon=None,
                        options=["Current Opportunities", "Competitor Info", "Forecast Recompetes"])
if view == "Current Opportunities":
    with st.sidebar:
        awarding_agency = st.multiselect(label="Agency",
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
    if awarding_agency:
        filtered_df = filtered_df[filtered_df["Awarding_Agency"].isin(awarding_agency)]
    if opp_type:
        filtered_df = filtered_df[filtered_df["Type"].isin(opp_type)]
    if ecs_rating:
        filtered_df = filtered_df[filtered_df["Score"].isin(ecs_rating)]
    if set_aside_type:
        filtered_df = filtered_df[filtered_df["Set_Aside_Type"].isin(set_aside_type)]
    if days_remaining:
        filtered_df = filtered_df[filtered_df["DaysRemainingCode"].isin(days_remaining)]

    # ------------------------------------ KPIs ----------------------------------------

    total_opportunities, days_to_respond, count_positive_ecs, count_green = current_opportunities_kpis(filtered_df)

    kpi_row_page1 = st.columns(4)

    kpi_row_page1[0].metric(label="Total Opportunities", value=f"{total_opportunities}")
    kpi_row_page1[1].metric(label="Avg. Days to Respond", value=f"{days_to_respond:.1f}")
    kpi_row_page1[2].metric(label="Count of positive ECS Rating", value=f"{count_positive_ecs}")
    kpi_row_page1[3].metric(label="Opportunities with 25+ Days Remaining", value=f"{count_green}")

    # ------------------------------------ Charts ----------------------------------------
    first_chart_row_page1 = st.columns(2)
    # ------------------------------------ Opp by Type ----------------------------------------

    opp_by_type = filtered_df.groupby("Type").agg(
        {'Notice_ID': 'count', 'Days_to_ResponseDeadline': 'mean'}
    ).reset_index()
    opp_by_type = opp_by_type.sort_values("Days_to_ResponseDeadline", ascending=True)
    fig = bar_scatter_chart(data=opp_by_type, bar_X="Type", bar_Y="Notice_ID",
                            bar_name="Number of Opportunities", scatter_X="Type",
                            scatter_Y="Days_to_ResponseDeadline",
                            scatter_name="Avg. Days to Respond to Deadline",
                            title="OPPORTUNITY BY TYPE")

    first_chart_row_page1[0].plotly_chart(fig, use_container_width=True)
    # ------------------------------------ Opp by Agency ----------------------------------------

    opp_by_agency = filtered_df.groupby("Awarding_Agency")["Notice_ID"].count().reset_index()
    opp_by_agency = opp_by_agency.sort_values("Notice_ID", ascending=True)
    opp_by_agency['Awarding_Agency'] = opp_by_agency['Awarding_Agency'].str[
                                       :15]  # Truncate the "Awarding_Agency" column
    fig = bar_chart(data=opp_by_agency, y="Awarding_Agency", x="Notice_ID",
                    orient="h", title="OPPORTUNITY BY AWARDING AGENCIES", text="Notice_ID",
                    pre_hover_text="Number of Opportunities")

    first_chart_row_page1[1].plotly_chart(fig, use_container_width=True)
    # ------------------------------------ Opp by Posted Month ----------------------------------------

    opp_by_posted_date = filtered_df.groupby("Posted_Date")["Notice_ID"].count().reset_index()
    fig = scatter_plot(data=opp_by_posted_date, x="Posted_Date", y="Notice_ID",
                       title="OPPORTUNITY POSTED BY MONTH", name="Opportunity Count",
                       text="Notice_ID")
    first_chart_row_page1[0].plotly_chart(fig, use_container_width=True)

    # ----------------------------------- Avg. Days to Response to Deadline By NAICS --------------------

    avg_days_to_response_NAICS = filtered_df.groupby(
        "NAICSCodeDesc"
    )["Days_to_ResponseDeadline"].mean().reset_index()
    avg_days_to_response_NAICS = avg_days_to_response_NAICS.sort_values("Days_to_ResponseDeadline", ascending=True)
    avg_days_to_response_NAICS['NAICSCodeDesc'] = avg_days_to_response_NAICS['NAICSCodeDesc'].str[:15]
    avg_days_to_response_NAICS = avg_days_to_response_NAICS[:27]
    fig = bar_chart(data=avg_days_to_response_NAICS, y="NAICSCodeDesc", x="Days_to_ResponseDeadline",
                    orient="h", title="AVG. DAYS TO RESPONSE TO DEADLINE BY NAICS", text="Days_to_ResponseDeadline",
                    pre_hover_text="Avg. Days to Response")

    first_chart_row_page1[1].plotly_chart(fig, use_container_width=True)
    # ------------------------------------ Data Chart --------------------------------------
    table_columns = ["Awarding_Agency", "Title", "Type",
                     "Posted_Date", "Days_to_ResponseDeadline", "Description link",
                     "NAICSCodeDesc", "Set_Aside_Type", "Score"]
    fig = opportunities_table(data=filtered_df, columns=table_columns)
    st.plotly_chart(fig, use_container_width=True)

if view == "Competitor Info":
    with st.sidebar:
        agency_name = st.multiselect(label="Agency",
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
    if agency_name:
        filtered_past_awards = filtered_past_awards[filtered_past_awards["Awarding Agency"].isin(agency_name)]
    if awardee:
        filtered_past_awards = filtered_past_awards[filtered_past_awards["Recipient Name"].isin(awardee)]
    if contract_type:
        filtered_past_awards = filtered_past_awards[filtered_past_awards["Contract Award Type"].isin(contract_type)]
    if contract_status:
        filtered_past_awards = filtered_past_awards[filtered_past_awards["Contract Status"].isin(contract_status)]
    if award_amount_bins:
        filtered_past_awards = filtered_past_awards[filtered_past_awards["AwardAmount_Binned"].isin(award_amount_bins)]

    # ------------------------------------ KPIs ----------------------------------------

    total_past_awards, six_million_above, award_amount = competitor_kpis(data=filtered_past_awards)

    kpi_row_page2 = st.columns(3)

    kpi_row_page2[0].metric(label="Total Number of Past Awards", value=f"{total_past_awards}")
    kpi_row_page2[1].metric(label="Number of Awards Value $6+ Million", value=f"{six_million_above}")
    kpi_row_page2[2].metric(label="Total Past Award(s) Amount", value=f"${format_currency_label(award_amount)}")

    # ------------------------------------ Charts ----------------------------------------
    first_chart_row_page2 = st.columns(2)
    # ------------------------------------ Number of Awards By Recipient -----------------

    awards_by_recipient = filtered_past_awards.groupby("Recipient Name")["generated_internal_id"].count().reset_index()
    awards_by_recipient = awards_by_recipient.sort_values("generated_internal_id", ascending=True)
    awards_by_recipient.rename(columns={"generated_internal_id": "Number of Awards"}, inplace=True)
    awards_by_recipient = awards_by_recipient[:10]

    fig = pie_chart(data=awards_by_recipient, values="Number of Awards",
                    names="Recipient Name", title="NUMBER OF PAST AWARDS BY RECIPIENTS",
                    text_info="percent+value")

    first_chart_row_page2[0].plotly_chart(fig, use_container_width=True)
    # ------------------------------------ Amount of Awards By Recipient ----------------------------------------

    awards_amount_by_recipient = filtered_past_awards.groupby("Recipient Name")["Award Amount"].sum().reset_index()
    awards_amount_by_recipient['Formatted Award Amount'] = awards_amount_by_recipient['Award Amount'].apply(
        format_currency_label)
    awards_amount_by_recipient = awards_amount_by_recipient[:10]

    fig = pie_chart(data=awards_amount_by_recipient, values="Award Amount",
                    names="Recipient Name", title="PAST AWARDS AMOUNT BY RECIPIENTS",
                    text_info="percent")

    first_chart_row_page2[1].plotly_chart(fig, use_container_width=True)
    # ------------------------------------ Award Amount Chart ----------------------------------------

    award_amount_df = filtered_past_awards.groupby("Awarding Agency").agg(
        {'Award ID': 'count', 'Award Amount': 'sum'}
    ).reset_index()
    award_amount_df['Award Amount'] = award_amount_df['Award Amount'].apply(
        format_currency_label)
    award_amount_df.rename(columns={"Award ID": "Number of Awards"}, inplace=True)

    fig = table_chart(award_amount_df,
                      title="PAST AWARDS AMOUNT BY AWARDING AGENCY")
    first_chart_row_page2[0].plotly_chart(fig, use_container_width=True)

    # ------------------------------------ Award Amount Chart#2 ----------------------------------------
    award_amount_by_recp_naics_df = filtered_past_awards.groupby(
        ["naics_description", "Awarding Agency"]
    )['Award Amount'].sum().reset_index()
    award_amount_by_recp_naics_df = award_amount_by_recp_naics_df.sort_values(by="Award Amount", ascending=False)
    award_amount_by_recp_naics_df['Award Amount'] = award_amount_by_recp_naics_df['Award Amount'].apply(
        format_currency_label)
    award_amount_by_recp_naics_df.rename(columns={"naics_description": "NAICS"}, inplace=True)

    fig = table_chart(award_amount_by_recp_naics_df,
                      title="PAST AWARDS AMOUNT BY NAICS AND RECIPIENT")
    first_chart_row_page2[1].plotly_chart(fig, use_container_width=True)

    tables = awards_table(data=filtered_past_awards,
                          columns=["Award ID", "Awarding Agency", "Recipient Name",
                                   "AwardAmount_Binned", "Award Amount",
                                   "Start Date", "End Date", "Last Modified Date",
                                   "Months Until Contract Ends", "PastAwards_URL"])

    st.plotly_chart(tables, use_container_width=True)

if view == "Forecast Recompetes":
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

    contracts_count, average_offers_per_contract, contracts_value = contracts_kpis(data=filtered_contracts_data)
    kpi_row_page3 = st.columns(3)

    kpi_row_page3[0].metric(label="Count of Contracts", value=f"{contracts_count}")
    kpi_row_page3[1].metric(label="Avg. Offers Per Contract", value=f"{average_offers_per_contract:.2f}")
    kpi_row_page3[2].metric(label="Contract(s) Value", value=f"${format_currency_label(contracts_value)}")

    # ------------------------------------ Charts ----------------------------------------
    first_chart_row_page3 = st.columns(2)
    # --------------------- Award Amount By Months Until Contract Ends -------------------

    award_amount_by_months = filtered_contracts_data.groupby(
        ["Months Until Contract Ends", "Recipient Name"]
    )["Award Amount"].sum().reset_index()
    award_amount_by_months["Symbol"] = "diamond"
    award_amount_by_months = award_amount_by_months[
        award_amount_by_months["Months Until Contract Ends"] != "Contract/s Expired"
        ]
    fig = binned_scatter_plot(data=award_amount_by_months, x="Months Until Contract Ends",
                              y="Award Amount",
                              color="Recipient Name",
                              title="AWARD AMOUNT BY MONTHS UNTIL CONTRACT ENDS",
                              )

    first_chart_row_page3[0].plotly_chart(fig, use_container_width=True)
    # --------------------- Award Amount By Contract Duration (Years) -------------------

    award_amount_by_duration = filtered_contracts_data.groupby(
        ["Contract Duration (Years)", "Recipient Name"]
    )["Award Amount"].sum().reset_index()
    award_amount_by_duration["Symbol"] = "diamond"

    fig = binned_bar_chart(data=award_amount_by_duration, x="Contract Duration (Years)",
                           y="Award Amount", color="Recipient Name",
                           title="AWARD AMOUNT BY CONTRACT DURATION (Years)")

    first_chart_row_page3[1].plotly_chart(fig, use_container_width=True)
    # ------------------------------------ Filtered dataframe ----------------------------
    tables = forecast_table(data=filtered_contracts_data,
                            columns=["Award ID", "Awarding Agency", "Recipient Name",
                                     "naics_description", "Award Amount",
                                     "Start Date", "End Date", "Last Modified Date",
                                     "Months Until Contract Ends", "PastAwards_URL"])

    st.plotly_chart(tables, use_container_width=True)
