# F.O.A.M - Future Opportunity Assessment Manager

## Introduction

F.O.A.M (Future Opportunity Assessment Manager) is a dashboard designed to consolidate new government contract opportunities and past competitor successes into a single, accessible location. It aids users in spotting relevant contracts and assists in crafting proposals using previously successful strategies.

## Project Overview

This project is developed using Python and utilizes various libraries and tools, including:

- [Pandas](https://pandas.pydata.org/): For data manipulation and analysis.
- [Streamlit](https://streamlit.io/): For creating interactive web applications.

## Data Collection
The data for this project is collected using APIs provided by USAspending.gov. To download the required data, you can use the ./data/scraper.ipynb Jupyter Notebook. This notebook provides a steps to use the USAspending.gov API to fetch data and save it to CSV files.

#### Instructions
- Open the ./data/scraper.ipynb notebook in Jupyter Notebook or JupyterLab.
- Follow the instructions at sam.gov website to make an account and get the API key.
- You can also update the parameters dictionary to get data according to your preferences.
- Run the notebook cells to fetch the data and save it to CSV files in the ./data/ directory.
- **Make sure to review and comply with the terms and conditions of the USAspending.gov API when using the data.**


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