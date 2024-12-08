import pandas as pd
import numpy as np
from portfolio.portfolio import Portfolio
from mom_signal.mom_signal import MomentumSignal

from alive_progress import alive_bar

class Backtest(Portfolio, MomentumSignal):  
    cum_top_excess_w_ret = []
    cum_top_excess_l_ret = []
    cum_top_excess_arb_ret = []

    cum_bottom_excess_w_ret = []
    cum_bottom_excess_l_ret = []
    cum_bottom_excess_arb_ret = []

    winner_top_port_list = []
    loser_top_port_list = []

    loser_bottom_port_list = []
    winner_bottom_port_list = []

    win_counts_top = []
    lose_counts_top = []
    
    win_counts_bottom = []
    lose_counts_bottom = []
    
    def __init__(self, portfolio: Portfolio):
            self.portfolio = portfolio 
    
    def run(self): 
        past_formation_dfs, future_holding_dfs = self.portfolio.get_walk_forward_splits()
        formed_portfolio_list = self.portfolio.get_formed_portfolio()
        
        future_holding_idx = pd.concat(future_holding_dfs).index
        cap_groups = ['Top', 'Bottom']
        portfolio_groups = ['Winner', 'Loser', 'Arbitrage']
        mom_groups = ['CMOM', 'MMOM', 'TMOM', 'PMOM']
        
        performance_idx = pd.MultiIndex.from_product([
                future_holding_idx,
                cap_groups,
                portfolio_groups,
                mom_groups
        ])
        
        performance_df = pd.DataFrame(np.nan, index=performance_idx, columns=['r'])
            
        # Run Backtest
        print("Backtest is running ...")
        with alive_bar(len(past_formation_dfs), force_tty=True) as bar: 
            for i in range(len(past_formation_dfs)):
                # Get formation period
                mask_fields = ['r', 'benchmark', 'log_mcap']
                df_selected = past_formation_dfs[i].stack(future_stack=True).loc[self.idx[:, formed_portfolio_list[i]], :]
                df_selected = df_selected[mask_fields]

                # Calculate Momentum Mesures
                df_selected['CMOM'] = df_selected.groupby(level=1)['r'].transform(lambda x: self.calculate_cmom(x))
                df_selected['MMOM'] = df_selected.groupby(level=1)['r'].transform(lambda x: self.calculate_mmom(x))
                df_selected['TMOM'] = df_selected.groupby(level=1)['r'].transform(lambda x: self.calculate_tmom(x))
                df_selected['PMOM'] = self.calculate_pmom(df_selected)

                # Fomation Portfolio
                N = len(formed_portfolio_list[i])

                N_top = N_bottom =round(.3*N)
                
                top_30 = df_selected.dropna().nlargest(N_top, 'log_mcap')
                bottom_30 = df_selected.dropna().nsmallest(N_bottom, 'log_mcap')

                mom_top_30 = top_30[['CMOM', 'MMOM', 'TMOM', 'PMOM']]
                mom_bottom_30 = bottom_30[['CMOM', 'MMOM', 'TMOM', 'PMOM']]

                # cap = df_selected.dropna()[['log_mcap']]

                avg_top_30 = mom_top_30.mean()
                avg_bottom_30 = mom_bottom_30.mean()

                weights_top_30 = (mom_top_30
                        .sub(avg_top_30)
                        .div(N_top)
                        .rename(
                                columns={
                                        'CMOM': 'CMOM_top_weight',
                                        'MMOM': 'MMOM_top_weight',
                                        'TMOM': 'TMOM_top_weight',
                                        'PMOM': 'PMOM_top_weight'
                                }
                        ))

                weights_bottom_30 = (mom_bottom_30
                        .sub(avg_bottom_30)
                        .div(N_bottom)
                        .rename(
                                columns={
                                        'CMOM': 'CMOM_bottom_weight',
                                        'MMOM': 'MMOM_bottom_weight',
                                        'TMOM': 'TMOM_bottom_weight',
                                        'PMOM': 'PMOM_bottom_weight'
                                }
                        ))

                winner_top_portfolio = weights_top_30.map(lambda x: x if x > 0 else 0)
                winner_bottom_portfolio = weights_bottom_30.map(lambda x: x if x > 0 else 0)

                loser_top_portfolio = weights_top_30.map(lambda x: abs(x) if x < 0 else 0)
                loser_bottom_portfolio = weights_bottom_30.map(lambda x: abs(x) if x < 0 else 0)
                
                self.winner_top_port_list.append(winner_top_portfolio)
                self.winner_bottom_port_list.append(winner_bottom_portfolio)
                self.loser_top_port_list.append(loser_top_portfolio)
                self.loser_bottom_port_list.append(loser_bottom_portfolio)


                # Calculate future holding return
                ret = future_holding_dfs[i].loc[:, self.idx[:, formed_portfolio_list[i]]].stack(future_stack=True)[['r']]
                benchmark = future_holding_dfs[i]['benchmark'].iloc[0, 0]

                top_ret = ret.loc[self.idx[:, top_30.index.get_level_values(1)], :]
                bottom_ret = ret.loc[self.idx[:, bottom_30.index.get_level_values(1)], :]

                w_top_ret = (winner_top_portfolio
                        .mul(top_ret.values.reshape(N_top, 1), axis='columns')
                        .mul(100)
                        .rename(columns={
                                        'CMOM_weight': 'CMOM_top_ret',
                                        'MMOM_weight': 'MMOM_top_ret',
                                        'TMOM_weight': 'TMOM_top_ret',
                                        'PMOM_weight': 'PMOM_top_ret'
                                        }                
                        )) # Unit: percentage

                w_bottom_ret = (winner_bottom_portfolio
                        .mul(bottom_ret.values.reshape(N_bottom, 1), axis='columns')
                        .mul(100)
                        .rename(columns={
                                        'CMOM_weight': 'CMOM_bottom_ret',
                                        'MMOM_weight': 'MMOM_bottom_ret',
                                        'TMOM_weight': 'TMOM_bottom_ret',
                                        'PMOM_weight': 'PMOM_bottom_ret'
                                        }                
                        )) # Unit: percentage

                l_top_ret = (loser_top_portfolio
                        .mul(top_ret.values.reshape(N_top, 1), axis='columns')
                        .mul(100)
                        .rename(columns={
                                        'CMOM_weight': 'CMOM_top_ret',
                                        'MMOM_weight': 'MMOM_top_ret',
                                        'TMOM_weight': 'TMOM_top_ret',
                                        'PMOM_weight': 'PMOM_top_ret'
                                        }                
                        )) # Unit: percentange

                l_bottom_ret = (loser_bottom_portfolio
                        .mul(bottom_ret.values.reshape(N_bottom, 1), axis='columns')
                        .mul(100)
                        .rename(columns={
                                        'CMOM_weight': 'CMOM_bottom_ret',
                                        'MMOM_weight': 'MMOM_bottom_ret',
                                        'TMOM_weight': 'TMOM_bottom_ret',
                                        'PMOM_weight': 'PMOM_bottom_ret'
                                        }                
                        )) # Unit: percentange

                arb_top_ret = ((w_top_ret - l_top_ret)
                        .rename(columns={
                                        'CMOM_weight': 'CMOM_top_ret',
                                        'MMOM_weight': 'MMOM_top_ret',
                                        'TMOM_weight': 'TMOM_top_ret',
                                        'PMOM_weight': 'PMOM_top_ret'  
                                        }
                        ))  # Unit: percentage

                arb_bottom_ret = ((w_bottom_ret - l_bottom_ret)
                        .rename(columns={
                                        'CMOM_weight': 'CMOM_bottom_ret',
                                        'MMOM_weight': 'MMOM_bottom_ret',
                                        'TMOM_weight': 'TMOM_bottom_ret',
                                        'PMOM_weight': 'PMOM_bottom_ret'  
                                        }
                        ))  # Unit: percentage

                w_top_excess_ret = w_top_ret.sum() #- benchmark
                l_top_excess_ret = l_top_ret.sum() #- benchmark
                arb_top_excess_ret = arb_top_ret.sum() #- benchmark
                
                w_bottom_excess_ret = w_bottom_ret.sum() #- benchmark
                l_bottom_excess_ret = l_bottom_ret.sum() #- benchmark
                arb_bottom_excess_ret = arb_bottom_ret.sum() #- benchmark
                self.cum_top_excess_w_ret.append(w_top_excess_ret.values)
                self.cum_top_excess_l_ret.append(l_top_excess_ret.values)
                self.cum_top_excess_arb_ret.append(arb_top_excess_ret.values)
                
                self.cum_bottom_excess_w_ret.append(w_bottom_excess_ret.values)
                self.cum_bottom_excess_l_ret.append(l_bottom_excess_ret.values)
                self.cum_bottom_excess_arb_ret.append(arb_bottom_excess_ret.values)
                bar() 
