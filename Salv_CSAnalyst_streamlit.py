#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import os

# Set page config
st.set_page_config(page_title="Financial Data Analysis", layout="wide")

# Title
st.title("Financial Data Analysis Dashboard")

# QUESTION 1
st.header("QUESTION 1")
st.markdown("""
Tell me about a problem you had to solve at work. What was the problem, and how did you solve it? 

Every project comes with its own problems. Together with the data Engineer team, the goal was to create pipelines and build predictive models for optimizing pricing strategies in different market segments with different segmented participants. Most data are in a relational database, but a particular one exists in the NoSQL database. It is real-time data on Google Firebase. The problem was that it exist in different formats and on different platforms. I assisted the team in developing a dashboard with Streamlite to draw insight and extract real-time info from the Database with API and Python skills. I employed in-depth research to understand how the database works and work alongside another team member. My contribution was impactful and helped the team to deliver a bespoke platform that employs real-time and historical data to solve problems. 
""")

# QUESTION 2
st.header("QUESTION 2")
st.markdown("""
How have you used tabular data previously?

Yes, my experience in data analysis has exposed me to a large array of data sets, use advanced Excel skills, and SQL to query databases, and manipulate and clean large data. My Background in Quantitative Economics has also equipped me with data modeling, visualization and advanced research skills
""")

# QUESTION 3
st.header("QUESTION 3")
st.markdown("""
Unfortunately, financial data is often messy, and ensuring its accuracy is critical. In this case, we need to verify the uniqueness of account numbers and check that the data is logical (e.g., a customer's age cannot be 150 years). This ensures transactions are correctly counted, and the right connections are made. Attached is an example of transaction data that contains common data issues. Please describe your approach to checking data quality and identify any problems you detect in the dataset. Additionally, please provide the SQL queries you would use, if applicable.
""")

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Load CSV into DataFrame
    df = pd.read_csv(uploaded_file)

    # Create an in-memory SQLite database
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()

    # Load DataFrame into SQL table
    df.to_sql('transactions', conn, index=False, if_exists='replace')

    st.subheader("Data Overview")
    st.dataframe(df.head())

    # STEP2. Check for missing values
    st.subheader("Missing Values Analysis")
    query_missing_values = """
    SELECT 
      COUNT(*) - COUNT(id) AS missing_id,
      COUNT(*) - COUNT(date_created) AS missing_date,
      COUNT(*) - COUNT(sender_account) AS missing_senderaccount,
      COUNT(*) - COUNT(receiver_account) AS missing_receiveraccount,
      COUNT(*) - COUNT(status) AS missing_status,
      COUNT(*) - COUNT(original_amount) AS missing_original_amount,
      COUNT(*) - COUNT(amount) AS missing_amount,
      COUNT(*) - COUNT(sender_name) AS missing_sender_name,
      COUNT(*) - COUNT(receiver_name) AS missing_receiver_name,
      COUNT(*) - COUNT(from_cur) AS missing_from_cur,
      COUNT(*) - COUNT(to_cur) AS missing_to_cur,
      COUNT(*) - COUNT(cur_rate) AS missing_cur_rate,
      COUNT(*) - COUNT(refrence) AS missing_reference,
      COUNT(*) - COUNT(type) AS missing_type
    FROM transactions;
    """
    missing_values = pd.read_sql_query(query_missing_values, conn)
    st.write("Missing values:")
    st.dataframe(missing_values)

    # STEP3. Check for duplicate transactions
    st.subheader("Duplicate Transactions")
    query_duplicates = """
    SELECT id, COUNT(*) as count
    FROM transactions
    GROUP BY id
    HAVING COUNT(*) > 1;
    """
    duplicates = pd.read_sql_query(query_duplicates, conn)
    st.write("Duplicate transactions:")
    st.dataframe(duplicates)

    # STEP4. Check for mismatched currencies
    st.subheader("Mismatched Currencies")
    query_mismatched_currencies = """
    SELECT *
    FROM transactions
    WHERE from_cur = to_cur;
    """
    mismatched_currencies = pd.read_sql_query(query_mismatched_currencies, conn)
    st.write("Mismatched currencies:")
    st.dataframe(mismatched_currencies)

    # STEP5. Check for incorrect currency conversions
    st.subheader("Incorrect Currency Conversions")
    query_currency_conversion = """
    SELECT 
        id,
        sender_account,
        receiver_account,
        original_amount,
        amount AS amount_received,
        from_cur,
        to_cur,
        cur_rate,
        ABS(original_amount * cur_rate - amount) AS conversion_difference,
        ABS(original_amount * cur_rate) AS Exchange_rate_Calculated_amount
    FROM 
        transactions
    WHERE 
        from_cur != to_cur
        AND ABS(original_amount * cur_rate - amount) > 0.01
    ORDER BY 
        conversion_difference DESC;
    """
    currency_conversion_issues = pd.read_sql_query(query_currency_conversion, conn)
    st.write("Incorrect currency conversions:")
    st.dataframe(currency_conversion_issues)

    # Export to CSV
    csv = currency_conversion_issues.to_csv(index=False)
    st.download_button(
        label="Download Currency Conversion Issues",
        data=csv,
        file_name="currency_conversion_issues.csv",
        mime="text/csv",
    )

    # STEP7. Check for outliers in exchange rates
    st.subheader("Exchange Rate Outliers")
    query_exchange_rate_outliers = """
    SELECT *
    FROM transactions
    WHERE cur_rate < 0.01 OR cur_rate > 10;
    """
    exchange_rate_outliers = pd.read_sql_query(query_exchange_rate_outliers, conn)
    st.write("Exchange rate outliers:")
    st.dataframe(exchange_rate_outliers)

    # VISUALIZATION
    st.header("VISUALIZATION")

    # Plot exchange rates
    st.subheader("Exchange Rates by Source Currency")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(x='from_cur', y='cur_rate', data=df, ax=ax)
    plt.title('Exchange Rates by Source Currency')
    plt.xlabel('Source Currency')
    plt.ylabel('Exchange Rate')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

    # Plot missing values
    st.subheader("Missing Values by Column")
    fig, ax = plt.subplots(figsize=(12, 6))
    missing_values.T.plot(kind='bar', ax=ax)
    plt.title('Missing Values by Column')
    plt.xlabel('Columns')
    plt.ylabel('Number of Missing Values')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

else:
    st.write("Please upload a CSV file to begin the analysis.")

