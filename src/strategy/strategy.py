import pandas as pd
import numpy as np
from hdbscan import HDBSCAN
from sklearn.preprocessing import StandardScaler

class AbnormalMomentumStatey: 
    def __hyperparameter_search(scaled_feature): 
        results = []

        min_sample_grid = np.arange(5, 35)
        min_cluster_size_grid = np.arange(5, 35)

        for min_sample in min_sample_grid: 
            for min_cluster_size in min_cluster_size_grid: 
                
                clf = HDBSCAN(min_samples=min_sample, min_cluster_size=min_cluster_size, core_dist_n_jobs=8)
                clf.fit(scaled_feature)
                
                if len(clf.cluster_persistence_) == 0:
                    continue
                
                results.append([min_sample, min_cluster_size, clf.cluster_persistence_.mean()]) 
        
        return sorted(results, key=lambda x : x[-1], reverse=True)[0]
    
    @classmethod
    def find_cluster(self, formed_portfolio): 
        feature_cols = ['CMOM', 'MMOM', 'TMOM', 'PMOM']
        
        feature = formed_portfolio[feature_cols].values

        sc = StandardScaler()
        scaled_feature = sc.fit_transform(feature)
        
        best_min_sample, best_min_cluster_size, _ = self.__hyperparameter_search(scaled_feature)
        
        clf = HDBSCAN(min_samples=best_min_sample, min_cluster_size=best_min_cluster_size, core_dist_n_jobs=8)
        clf.fit(scaled_feature)
        
        return clf.labels_