import pandas as pd
import dask.dataframe as dd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from functools import reduce

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

from glob import glob
import time

pd.set_option('display.float_format', '{:.6f}'.format)
np.set_printoptions(suppress=True)
pio.templates.default = 'plotly_white'


