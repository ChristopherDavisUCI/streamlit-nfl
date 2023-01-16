import numpy as np
import pandas as pd

df_names = pd.read_csv("/Users/christopherdavis/Dropbox/Programming/NFLdata/NameReplacements.csv")
df_names.set_index("Long", drop=True, inplace=True)
series_names = df_names["Short"]

df_div = pd.read_csv("/Users/christopherdavis/Dropbox/Programming/NFLdata/divisions.csv")
df_div.columns = ["team", "div"]
ser_div = df_div.set_index("team")["div"]

def get_div(team):
    return ser_div[team]

def get_conf(team):
    return ser_div[team][:3]

def prob_to_odds(p):
    if p < .000001:
        return np.nan
    if p > .999999:
        return np.nan
    if p > 0.5:
        x = 100*p/(p-1)
        return f"{x:.0f}"
    elif p <= 0.5:
        x = 100*(1-p)/p
        return f"+{x:.0f}"

def odds_to_prob(x):
    x = float(x)
    if x < 0:
        y = -x
        return y/(100+y)
    else:
        return 100/(100+x)
    
def get_abbr(long):
    long = long.upper()
    if long in series_names.index:
        return series_names[long]
    temp = long.split()[-1]
    if temp in series_names.index:
        return series_names[temp]
