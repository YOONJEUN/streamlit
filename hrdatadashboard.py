import streamlit as st
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib

df = pd.read_csv("./HR Data.csv")
df.head(10)


total_employees = len(df)
total_attritions = df['퇴직'].sum()
overall_rate = round(df['퇴직'].mean() * 100 , 1)