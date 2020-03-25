import pandas as pd
import numpy as np
import streamlit as st
import datetime as dt
import plotly.graph_objs as go


def cumulative_value(initial_price, pct_change_lst):

    res = [initial_price*(1 + pct_change_lst[0])]

    for i in range(1, len(pct_change_lst)):
        res.append(res[i-1] * (1 + pct_change_lst[i]))

    return res


def calc_cagr(price_df, column, date_col="DATE"):

    start_date = price_df[date_col].iloc[0]
    end_date = price_df[date_col].iloc[-1]

    start_price = price_df[column].iloc[0]
    end_price = price_df[column].iloc[-1]

    num_years = end_date.year - start_date.year

    res = (end_price/start_price)**(1/num_years) - 1

    return res


price_index_types = ["real","nominal"]


st.header("Housing Price Analysis")

index_type = st.sidebar.radio("Type", price_index_types, index=0)
initial_purchase_price = st.sidebar.number_input("Purchase Price", min_value=1, value=500000)
date_purchased = st.sidebar.date_input("Date Purchased", value=dt.date(1988, 1, 1))
show_raw_data = st.sidebar.checkbox("Show Raw Data", value=True)


### Import file
prop_prices_df = pd.read_csv("data/real_residential_prices_my.csv", parse_dates=["DATE"])
prop_prices_df = prop_prices_df.rename(columns={"QMYR628BIS" : index_type})

# forward/backward compounding
forward_prices_df = prop_prices_df[prop_prices_df["DATE"] > pd.Timestamp(date_purchased)]
backward_prices_df = prop_prices_df[prop_prices_df["DATE"] <= pd.Timestamp(date_purchased)]

gap_value = (backward_prices_df[index_type].iloc[-1] - forward_prices_df[index_type].iloc[0])\
                    /forward_prices_df[index_type].iloc[0]

backward_pct_change = backward_prices_df[index_type].pct_change(-1).fillna(gap_value)
forward_pct_change = forward_prices_df[index_type].pct_change().fillna(0)

prop_prices_df["tmp_pct_change"] = backward_pct_change.append(forward_pct_change)

forward_cumu = cumulative_value(initial_purchase_price, forward_pct_change.values)
backward_cumu = cumulative_value(initial_purchase_price, list(backward_pct_change.values)[::-1])
backward_cumu = backward_cumu[::-1]
test_values = backward_cumu + forward_cumu
prop_prices_df["cumu_capital"] = test_values

cumu_fig = go.Figure()

cumu_fig.add_trace(
    go.Scatter(
        x=prop_prices_df["DATE"],
        y=prop_prices_df["cumu_capital"],
        name="House Price"
    )
)

cumu_fig.update_layout(
    title = "Capital Growth",
    xaxis_title="Date",
    yaxis_title="Price"
)

cumu_fig

cagr = calc_cagr(prop_prices_df, "cumu_capital")
cagr

if show_raw_data:
    prop_prices_df


