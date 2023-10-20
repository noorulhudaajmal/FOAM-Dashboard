# F.O.A.M - Future Opportunity Assessment Manager

## Introduction

F.O.A.M (Future Opportunity Assessment Manager) is a dashboard designed to consolidate new government contract opportunities and past competitor successes into a single, accessible location. It aids users in spotting relevant contracts and assists in crafting proposals using previously successful strategies.

## Project Overview

This project is developed using Python and utilizes various libraries and tools, including:

- [Pandas](https://pandas.pydata.org/): For data manipulation and analysis.
- [Streamlit](https://streamlit.io/): For creating interactive web applications.
- [Streamlit Option Menu](https://pypi.org/project/streamlit-option-menu/): A Streamlit extension for creating option menus.
- Custom utility functions from `utils.py`.

## Project Structure

The project's main code file is the Streamlit application, where the dashboard is created and interactive visualizations are displayed. The application is structured into sections:

### Data Loading

Data from CSV files ("ActiveOpportunities.csv" and "PastAwards.csv") is loaded into Pandas DataFrames for analysis and visualization.

### Data Pre-processing

Data from CSV files undergo pre-processing to ensure it is in a suitable format for analysis and visualization. Date fields are converted to datetime objects, and various data manipulations are performed.

### Menu

The user can select different views from the menu, including 
- Home Page
- Current Opportunities
- Competitor Info
- Forecast Recompetes


### Home Page

The Home Page view provides a brief introduction to the dashboard and displays key metrics and visualizations.

### Current Opportunities

This view allows users to filter and analyze current government contract opportunities. Users can filter by agency, opportunity type, ECS rating, set-aside type, and days remaining.

### Competitor Info

The Competitor Info view allows users to analyze past awards and competitors. Users can filter by agency, awardee, contract type, contract status, and award amount bins.

### Forecast Recompetes

In this view, users can analyze future contract opportunities. Filters include agency, incumbent name, contract status, and months until contract ends.

## Installation and Setup

To run this project locally, follow these steps:

1. Install the required Python libraries using `pip install -r requirements.txt`.
2. Run the Streamlit application using `streamlit run app.py`.


---