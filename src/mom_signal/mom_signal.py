import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

class MomentumSignal:
    
    # 1. Functions used to calculate cross-sectional momentum
    @staticmethod
    def calculate_cmom(x: pd.Series): 
        """Method used to calculate cross-sectional momentum

        Args:
            x (pd.Series): Periodic performance for each stock

        Returns:
            pd.Series: Cross-sectional momentum signal
        """
        R = 1 + x
        cmom = (R.rolling(window=11).apply(np.prod,raw=True)) - 1
        
        return cmom

    # 2. Functions used to Calculate moving-average momentum
    @staticmethod
    def map_mmom(x: pd.api.typing.DataFrameGroupBy):
        """Method used to map rolling window to the difference between short-term and long-term performance

        Args:
            x (pd.api.typing.DataFrameGroupBy): _description_

        Returns:
            pd.Series: The difference between short-term and long-term performance
        """
        SP = x[-1] - 1
        LP = x.prod() - 1
        
        return SP - LP

    @staticmethod
    def calculate_mmom(x: pd.Series): 
        """Method used to calculate moving-average momentum

        Args:
            x (pd.Series): Periodic performance for each stock

        Returns:
            pd.Series: Moving-average momentum signal
        """
        R = 1 + x

        # Rolling Calculation
        mmom = R.rolling(window=11).apply(MomentumSignal.map_mmom, raw=True)
        
        return mmom

    # 3. Functions used to calculate time series momentum
    def map_tmom(self, x: np.ndarray):
        """_summary_

        Args:
            x (np.ndarray): _description_

        Returns:
            _type_: _description_
        """
        
        m = range(1, len(x)+1)
        
        # Calculate average signal
        s = np.array([np.sign(((x[:(i+1)] * m[:(i+1)]).sum()) / m[i]) for i in range(len(m))])
        average_s = s.sum() / len(m)
        
        # Calculate average time-weighted return
        ts = np.array([((x[:(i+1)] * m[:(i+1)]).sum()) / m[i] for i in range(len(m))])
        average_ts = ts.sum() / len(m)
        
        return np.abs(average_ts)*average_s

    def calculate_tmom(self, x: pd.Series): 
        
        # Rolling Calculation
        tmom = x.rolling(window=11).apply(self.map_tmom, raw=True)
        
        return tmom

    # 4. Functions used to calculate principle component momentum 
    def calculate_pmom(self, x: pd.DataFrame): 

        # Standardize data
        features = x[['CMOM', 'MMOM', 'TMOM']].dropna()
        sc = StandardScaler() 
        features_scaled = sc.fit_transform(features.values)

        # Calculate principle-components momentum
        pca = PCA(n_components=1)
        pca.fit(features_scaled)
        v = pca.components_

        # v.reshape(-1)
        pmom = (x[['CMOM','MMOM','TMOM']] 
                .dot(v.T)
                .rename(columns={0: 'PMOM'})
                ).PMOM
        
        return pmom