import sys
# import fireducks.pandas as pd
import pandas as pd

sys.path.append('../../src')
from analytics.returns import calculate_portfolio_return
from analytics.plots import visualize_cummulative_returns
from analytics.portfolio_statistics import create_portfolio_statistics

import streamlit as st

st.set_page_config(
    layout='wide'
)
st.title('Performnace Dashboard')
    
portfolio_types = ['non_abnormal', 'abnormal', 'exclude_abnormal']

for portfolio_type in portfolio_types: 
    performance_df = pd.read_csv(f'../performance/{portfolio_type}_performnace.csv', index_col=['time', 'ticker', 'cap_groups'], parse_dates=True)
    cummulative_winner_performance, cummulative_loser_performance, cummulative_arbitrage_performace = calculate_portfolio_return(performance_df)
    
    fig = visualize_cummulative_returns(cummulative_winner_performance, cummulative_loser_performance, cummulative_arbitrage_performace)
    
    _, loser_performance, _ = calculate_portfolio_return(performance_df, cummulative=False)
    
    
    performance_stats = create_portfolio_statistics(loser_performance)
    
    col1, col2 = st.columns([2, 1])
    with col1: 
        col1.subheader(f"Cummulative Return ({portfolio_type.replace("_", " ").capitalize()})")
        col1.plotly_chart(fig, use_container_width=True)
        
    with col2:
        col2.subheader(f"Portfolio statistics ({portfolio_type.replace("_", " ").capitalize()}) Loser")
        col2.table(performance_stats)  