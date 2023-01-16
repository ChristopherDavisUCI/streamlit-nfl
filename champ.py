import streamlit as st
import pandas as pd
import numpy as np

from itertools import product

from odds_helper import odds_to_prob, prob_to_odds

st.title('AFC Champion')

df = pd.read_csv("2023-div-rd.csv")
afc = df[df.Conf == "AFC"].set_index("Team")
afc_seeds = afc["Seed"]

df_spread_prob = pd.read_csv("spread_probs.csv")
ser_prob = df_spread_prob.set_index("Spread", drop=True)

def spread_to_prob(s):
    if isinstance(s, str):
        s = float(s)
    i = np.argmin(np.abs(ser_prob.index - s))
    return ser_prob.iloc[i].item()

def get_higher_seed(team1, team2):
    return team1 if afc_seeds[team1] < afc_seeds[team2] else team2

placeholder = st.empty()

use_prob = st.checkbox('Use probabilities instead of spreads')

if use_prob:
    placeholder.markdown(
"""Enter the probability (as a decimal between 0 and 1) of the higher seed winning. For example, if you enter 0.8 for KC vs BUF, that means 80% chance KC wins.""")
else:
    placeholder.markdown(
"""Enter the spread, with a **positive number meaning the higher seed is favored**. For example, if you enter -2 for KC vs BUF, that means you project Buffalo to be favored by 2, and if you enter 2.5, then you project KC to be favored by 2.5.""")

col1, col2, buff = st.columns([5,5,5])

def make_matchup(team1, team2):
    hteam = get_higher_seed(team1, team2)
    ateam = team1 if hteam == team2 else team2
    return st.text_input(f"{hteam} vs {ateam}")

div_pairs = [("KC", "JAX"), ("BUF", "CIN")]
teams = [team for pair in div_pairs for team in pair]

conf_pairs = list(product(*div_pairs))

val_dict = {}

with col1:
    st.write(f"Enter your predicted {'probability' if use_prob else 'spread'}.")
    st.subheader("Divisional round")
    for pair in div_pairs:
        res = make_matchup(*pair)
        val_dict[pair] = res
    if res != "":
        hteam = get_higher_seed(*pair)
        ateam = pair[0] if hteam == pair[1] else pair[1]
        p = float(res) if use_prob else spread_to_prob(res)
        st.write(f"Example: We estimate {hteam} has a {p:.0%} chance of beating {ateam} in the divisional round.")

with col2:
    st.subheader("Conference championship")
    for pair in conf_pairs:
        val_dict[pair] = make_matchup(*pair)



def get_team_prob(team, prob_dict):
    orig = next(pair for pair in div_pairs if team in pair)
    if get_higher_seed(*orig) == team:
        prob = prob_dict[orig]
    else:
        prob = 1 - prob_dict[orig]
    opp_pair = next(pair for pair in div_pairs if team not in pair)
    
    next_prob = 0
    for pair in conf_pairs:
        if team not in pair:
            continue
        if team == get_higher_seed(*pair):
            temp_prob = prob_dict[pair]
        else:
            temp_prob = 1-prob_dict[pair]
        opp = next(t for t in pair if t != team)
        if opp == get_higher_seed(*opp_pair):
            opp_prob = prob_dict[opp_pair]
        else:
            opp_prob = 1-prob_dict[opp_pair]
        next_prob += opp_prob*temp_prob
    
    return prob*next_prob


st.subheader("Estimated fair prices to be AFC Champion:")

if (len(val_dict) == 6) and all(v != "" for v in val_dict.values()):
    if use_prob:
        prob_dict = {k:float(v) for k,v in val_dict.items()}
    else:
        prob_dict = {k:spread_to_prob(v) for k,v in val_dict.items()}
    for team in teams:
        prob = get_team_prob(team, prob_dict)
        st.write(f"{team}: {prob_to_odds(prob)} (probability: {prob:.3f})")
else:
    st.write("(Be sure to enter all six values.)")
    
    
