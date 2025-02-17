import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def visualize_cummulative_returns(winner_performance, loser_performance, arbitrage_performance): 
    color_map = {
        'cmom_return': "#EEE8AA", 
        'mmom_return': "#20B2AA", 
        'tmom_return': "#DDA0DD", 
        'pmom_return': "#FF6F61"
    }

    fig = make_subplots(
        rows=3, 
        cols=3, 
        horizontal_spacing=0.03, 
        vertical_spacing=0.09,
        column_titles=['Winner Portfolio', 'Loser Portfolio', 'Arbitrage Portfolio'],
        row_titles=['Bottom', 'Mid', 'Top']
    )

    for i, cap_group in enumerate(['bottom', 'mid', 'top']): 
        for col in winner_performance.xs(cap_group, level=0).columns: 
            fig.add_trace(
                go.Scatter(
                    x=winner_performance.xs(cap_group, level=0).index,
                    y=winner_performance.xs(cap_group, level=0)[col],
                    name=f'{cap_group} {col}',
                    line=dict(color=color_map[col]),
                    showlegend=False
                ),
                row=i+1, 
                col=1
            )
            
        for col in loser_performance.xs(cap_group, level=0).columns: 
            fig.add_trace(
                go.Scatter(
                    x=loser_performance.xs(cap_group, level=0).index,
                    y=loser_performance.xs(cap_group, level=0)[col],
                    name=f'{cap_group} {col}',
                    line=dict(color=color_map[col]),
                    showlegend=False
                ),
                row=i+1, 
                col=2
            )
            
        for col in arbitrage_performance.xs(cap_group, level=0).columns: 
            fig.add_trace(
                go.Scatter(
                    x=arbitrage_performance.xs(cap_group, level=0).index,
                    y=arbitrage_performance.xs(cap_group, level=0)[col],
                    name=f'{cap_group} {col}',
                    line=dict(color=color_map[col]),
                    showlegend=False
                ),
                row=i+1,
                col=3
            )

    fig.update_layout(
        width=1400, 
        height=700,
        margin=dict(l=20, r=20, t=50, b=20),
        template='plotly_dark',
        autosize=True
    )

    return fig