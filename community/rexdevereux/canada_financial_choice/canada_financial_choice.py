import streamlit as st
import pandas as pd
import altair as alt

# --- Tax brackets, as provided ---
federal_brackets = [
    (0, 55867, 0.15),
    (55867, 111733, 0.205),
    (111733, 173205, 0.26),
    (173205, 246752, 0.29),
    (246752, float('inf'), 0.33)
]

provincial_brackets = {
    "Ontario": [(0, 49231, 0.0505), (49231, 98463, 0.0915), (98463, 150000, 0.1116), (150000, 220000, 0.1216), (220000, float('inf'), 0.1316)],
    "Alberta": [(0, 148269, 0.10), (148269, 177922, 0.12), (177922, 237230, 0.13), (237230, 355845, 0.14), (355845, float('inf'), 0.15)],
    "British Columbia": [(0, 45654, 0.0506), (45654, 91310, 0.077), (91310, 104835, 0.105), (104835, 127299, 0.1229), (127299, 172602, 0.147), (172602, float('inf'), 0.168)],
    "Quebec": [(0, 55780, 0.15), (55780, 111505, 0.20), (111505, 134095, 0.24), (134095, float('inf'), 0.2575)],
    "Manitoba": [(0, 45100, 0.108), (45100, 100000, 0.1275), (100000, float('inf'), 0.174)],
    "Saskatchewan": [(0, 50777, 0.105), (50777, 145212, 0.125), (145212, float('inf'), 0.145)],
    "Nova Scotia": [(0, 29590, 0.0879), (29590, 59180, 0.1495), (59180, 93000, 0.1667), (93000, 150000, 0.175), (150000, float('inf'), 0.21)],
    "New Brunswick": [(0, 49000, 0.094), (49000, 98000, 0.14), (98000, 162383, 0.16), (162383, float('inf'), 0.195)],
    "Newfoundland and Labrador": [(0, 41457, 0.087), (41457, 82913, 0.145), (82913, 148027, 0.158), (148027, float('inf'), 0.178)],
    "Prince Edward Island": [(0, 31984, 0.098), (31984, 63969, 0.138), (63969, float('inf'), 0.167)],
    "Northwest Territories": [(0, 50197, 0.059), (50197, 100392, 0.086), (100392, 163651, 0.122), (163651, float('inf'), 0.1405)],
    "Yukon": [(0, 55867, 0.064), (55867, 111733, 0.09), (111733, 173205, 0.109), (173205, 246752, 0.128), (246752, float('inf'), 0.15)],
    "Nunavut": [(0, 51279, 0.04), (51279, 102555, 0.07), (102555, 167275, 0.09), (167275, float('inf'), 0.115)]
}

# --- Tax calculator ---
def tax_calc(taxable_income, brackets):
    tax = 0.0
    for low, high, rate in brackets:
        if taxable_income > low:
            amt = min(high, taxable_income) - low
            tax += amt * rate
            if taxable_income < high:
                break
    return tax

def after_tax_income(salary, rrsp, province):
    ti = max(0, salary - rrsp)
    fed_tax = tax_calc(ti, federal_brackets)
    prov_tax = tax_calc(ti, provincial_brackets[province])
    return salary - fed_tax - prov_tax

# --- Streamlit App ---
st.set_page_config("After-Tax Income Canada", layout="centered")

st.title("Compare After-Tax Income Across Canadian Provinces (2025)")
st.write("Enter your details to see how much after-tax income you’d keep in each province. RRSP contributions reduce taxable income.")

salary = st.number_input("Annual Salary ($)", min_value=0, value=85000, step=1000)
rrsp = st.number_input("RRSP Contributions ($)", min_value=0, value=10000, step=1000)
province = st.selectbox("Province", list(provincial_brackets.keys()), index=0)

# Compute results for all provinces
results = []
for prov in provincial_brackets.keys():
    income = after_tax_income(salary, rrsp, prov)
    results.append({"Province": prov, "AfterTax": income, "Selected": prov == province})

df = pd.DataFrame(results)

# --- Altair chart ---
highlight_color = "#D80621"  # deep green
other_color = "#e1e5ea"      # pale gray

chart = (
    alt.Chart(df)
    .mark_bar(size=32)
    .encode(
        x=alt.X("Province", sort="-y"),
        y=alt.Y("AfterTax", title="After-Tax Income ($)", axis=alt.Axis(format="$,.0f")),
        color=alt.condition(
            alt.datum.Selected,
            alt.value(highlight_color),
            alt.value(other_color)
        ),
        tooltip=[
            alt.Tooltip("Province"),
            alt.Tooltip("AfterTax", format="$.0f", title="After-Tax Income"),
        ]
    )
    .properties(width=700, height=420)
)

st.altair_chart(chart, use_container_width=True)

# Show data table (optional)
with st.expander("See calculation table"):
    st.dataframe(df, hide_index=True)


