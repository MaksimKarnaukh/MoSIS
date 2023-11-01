import pandas as pd
import numpy as np


def calculate_sum_of_squared_errors(simulated_data, experimental_data):
    squared_errors = (simulated_data - experimental_data) ** 2
    sse = np.sum(squared_errors)
    return sse


def read_deceleration_data_csv():
    data = pd.read_csv('./input/deceleration_data.csv')
    return data['y'].values
