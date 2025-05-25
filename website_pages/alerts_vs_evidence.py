# libraries
import pandas as pd
import os
import streamlit as st
from itertools import product

# sklearn
from matplotlib import pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
import numpy as np

# typing
from typing import List
from typing import Optional

# helper imports
from utils.helper_functions import * 


# read data
# rename column for shell casing
# fillna values for casings, injuries and arrests.
# @st.cache_data
# def load_data_incidents():
#     df = (
#         pd.read_csv(
#             os.path.join(
#                 os.path.dirname("__file__"),
#                 "Data/2018-2024_cambridge_shotspotter_incidents - cambridge_shotspotter_incidents_extended_geocoded.csv",
#             ),
#             header=0,
#         )
#         .rename(columns={"shell_casings": "casings"})
#         .fillna({"casings": 0, "injuries": 0, "arrests": 0})
#     )

#     return df


# pipeline for all combinations & years
# @st.cache_data
# def year_alert_combinations_data_incidents():
#     # load all data to be used
#     df = load_data_incidents()

#     # change columns and clean data
#     df_summary = (
#         df.groupby(["year", "shotspotter_alert"])
#         .agg(
#             event_counts=pd.NamedAgg(aggfunc="count", column="additional_details"),
#             casings=pd.NamedAgg(column="casings", aggfunc="sum"),
#             injuries=pd.NamedAgg(column="injuries", aggfunc="sum"),
#             arrests=pd.NamedAgg(column="arrests", aggfunc="sum"),
#         )
#         .reset_index(drop=False)
#     )

#     # unique
#     # [python - Create all possible combinations of multiple columns in a Pandas DataFrame - Stack Overflow](https://stackoverflow.com/questions/49980763/create-all-possible-combinations-of-multiple-columns-in-a-pandas-dataframe#58903268)

#     columns_required = ["year", "shotspotter_alert"]
#     uniques = [df_summary[i].unique().tolist() for i in columns_required]
#     combinations_df = pd.DataFrame(product(*uniques), columns=columns_required)

#     # extract values
#     full_combinations_df = pd.merge(
#         combinations_df, df_summary, on=columns_required, how="right"
#     ).assign(
#         casings=lambda x: x.casings.fillna(0),
#         injuries=lambda x: x.injuries.fillna(0),
#         arrests=lambda x: x.arrests.fillna(0),
#     )

#     return full_combinations_df


# load data
# df = load_data_incidents()
df, _ = load_all_data()

# extract min and max for global sliders
year_range_min = df["year"].min()
year_range_max = df["year"].max()

# load combinations + years
full_combinations_df = year_alert_combinations_data_incidents()

# session state
if "data" not in st.session_state:
    st.session_state["data"] = df
if "select_year_slider" not in st.session_state:
    st.session_state["select_year_slider"] = (year_range_min, year_range_max)
if "selected_df_year" not in st.session_state:
    st.session_state["selected_df_year"] = full_combinations_df
if "jurisdiction" not in st.session_state:
    st.session_state["jurisdiction"] = False

# functions to load ans store session keys
def keep(key):
    # Copy from temporary widget key to permanent key
    st.session_state[key] = st.session_state["_" + key]


def unkeep(key):
    # Copy from permanent key to temporary widget key
    st.session_state["_" + key] = st.session_state[key]


# global slider
unkeep("select_year_slider")
st.sidebar.slider(
    "Select a range of values",
    min_value=year_range_min,
    max_value=year_range_max,
    # value = (year_range_min, year_range_max),
    key="_select_year_slider",
    on_change=keep,
    args=["select_year_slider"],
)

# global toggle
unkeep("jurisdiction")
st.sidebar.toggle(
    "Exclude other jurisdictions (e.g. MBTA, State Police etc.)",
    key="_jurisdiction",
    on_change=keep,
    args=['jurisdiction']
)

# apply toggle
if st.session_state["jurisdiction"]:
    df = df.loc[~df["additional_details"].str.lower().str.endswith("jurisdiction.")]

# update session data by filtering years
st.session_state["data"] = df[
    (df["year"] <= st.session_state["_select_year_slider"][1])
    & (df["year"] >= st.session_state["_select_year_slider"][0])
]

# update selected_df_year by filtering years
st.session_state["selected_df_year"] = full_combinations_df[
    (
        (full_combinations_df["year"] <= st.session_state["_select_year_slider"][1])
        & (full_combinations_df["year"] >= st.session_state["_select_year_slider"][0])
    )
]

# user selection for events on this tab
option_alert_event = st.sidebar.multiselect(
    "Please select what makes up a gun event (for this page only)",
    ["casings", "injuries", "arrests"],
    ["casings", "injuries", "arrests"],
)

# colourmap
cmap = st.sidebar.selectbox(
    "Colormap", ["Blues", "Greens", "Reds", "Purples", "Oranges", "Greys"]
)

list_column_events = [f"{x}_event" for x in option_alert_event]


# load state
def create_event_alert_data():
    # load data from state
    df_filtered = st.session_state["data"]

    df_event_alert = df_filtered.assign(
        casings_event=lambda x: x["casings"] > 0,
        injuries_event=lambda x: x["injuries"] > 0,
        arrests_event=lambda x: x["arrests"] > 0,
    )

    # create column from any of the selected columns
    df_event_alert["selected_event"] = df_event_alert[list_column_events].any(axis=1)

    return df_event_alert


# load data
df_event_alert = create_event_alert_data()

# create confusion matrix
# selected events are actual values
# shotspotter alerts are predicted values
#
cm_df = confusion_matrix(
    df_event_alert["selected_event"], df_event_alert["shotspotter_alert"]
)


# variables from binary classification
# TN_var = cm_df[0][0]
# FN_var = cm_df[1][0]
# TP_var = cm_df[1][1]
# FP_var = cm_df[0][1]

# use ravel
TN_var, FP_var, FN_var, TP_var = cm_df.ravel()

binary_classification_counts_dict = {
    "True Negative": TN_var,
    "False Positive": FP_var,
    "False Negative": FN_var,
    "True Positive": TP_var,    
}


# extra things to compute
# https://www.researchgate.net/figure/The-confusion-matrix-shows-the-counts-of-true-and-false-predictions-obtained-with-known_fig3_305716645


# @st.cache_data
def calculate_metrics(tp: int, fp: int, fn: int, tn: int) -> dict:
    try:
        accuracy = (tp + tn) / (tp + fp + fn + tn)
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        f1 = 2 * (precision * recall) / (precision + recall)
        false_negative_rate = fn / (tp + fn)
        false_positive_rate = fp / (fp + tn)
        specificity = tn / (fp + tn)
        false_discovery_rate = fp / (tp + fp)
        false_omission_rate = fn / (fn + tn)
        negative_predictive_rate = tn / (fn + tn)
    except ZeroDivisionError:
        accuracy = precision = recall = f1 = 0
        false_negative_rate = false_positive_rate = specificity = (
            false_discovery_rate
        ) = 0
        false_omission_rate = negative_predictive_rate = 0
    return {
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "False Negative Rate": false_negative_rate,
        "False Positive Rate": false_positive_rate,
        "Specificity": specificity,
        "False Discovery Rate": false_discovery_rate,
        "False Omission Rate": false_omission_rate,
        "Negative Predictive Rate": negative_predictive_rate,
        "Accuracy String": f"({tp} + {tn}) / ({tp} + {fp} + {fn} + {tn})"
        if accuracy != 0
        else "0",
        "Accuracy String 2": f"{tp + tn} / {tp + fp + fn + tn}"
        if accuracy != 0
        else "0",
        "Precision String": f"{tp} / ({tp} + {fp})" if precision != 0 else "0",
        "Precision String 2": f"{tp} / {tp + fp}" if precision != 0 else "0",
        "Recall String": f"{tp} / ({tp} + {fn})" if recall != 0 else "0",
        "Recall String 2": f"{tp} / {tp + fn}" if recall != 0 else "0",
        "F1 String": f"2 * {tp} / (2 * {tp} + {fp} + {fn})" if f1 != 0 else "0",
        "F1 String 2": f"{2*tp} / {2*tp + fp + fn}" if f1 != 0 else "0",
        "False Negative Rate String": f"{fn} / ({tp} + {fn})"
        if false_negative_rate != 0
        else "0",
        "False Negative Rate String 2": f"{fn} / {tp + fn}"
        if false_negative_rate != 0
        else "0",
        "False Positive Rate String": f"{fp} / ({fp} + {tn})"
        if false_positive_rate != 0
        else "0",
        "False Positive Rate String 2": f"{fp} / {fp + tn}"
        if false_positive_rate != 0
        else "0",
        "Specificity String": f"{tn} / ({fp} + {tn})" if specificity != 0 else "0",
        "Specificity String 2": f"{tn} / {fp + tn}" if specificity != 0 else "0",
        "False Discovery Rate String": f"{fp} / ({tp} + {fp})"
        if false_discovery_rate != 0
        else "0",
        "False Discovery Rate String 2": f"{fp} / {tp + fp}"
        if false_discovery_rate != 0
        else "0",
        "False Omission Rate String": f"{fn} / ({fn} + {tn})"
        if false_omission_rate != 0
        else "0",
        "False Omission Rate String 2": f"{fn} / {fn + tn}"
        if false_omission_rate != 0
        else "0",
        "Negative Predictive Rate String": f"{tn} / ({fn} + {tn})"
        if negative_predictive_rate != 0
        else "0",
        "Negative Predictive Rate String 2": f"{tn} / {fn + tn}"
        if negative_predictive_rate != 0
        else "0",
    }


# list values
list_values_primary = ["Accuracy", "Precision", "Recall", "F1"]

list_values_secondary = [
    "Specificity",
    "Negative Predictive Rate",
    "False Positive Rate",
    "False Discovery Rate",
]
list_values_tertiary = ["False Negative Rate", "False Omission Rate"]

st.header("Reports vs Alerts")

# counts
acol1, acol2, acol3, acol4 = st.columns(4)
for acol, metric, score in zip(
    (acol1, acol2, acol3, acol4),
    binary_classification_counts_dict.keys(),
    binary_classification_counts_dict.values(),
):
    with acol:
        st.metric(label=metric, value=round(score, 3))

# compute all metrics
metrics = calculate_metrics(TP_var, FP_var, FN_var, TN_var)

# subset metrics
brow_metrics = {k: metrics[k] for k in list_values_primary}

bcol1, bcol2, bcol3, bcol4 = st.columns(4)
for bcol, metric, score in zip(
    (bcol1, bcol2, bcol3, bcol4), brow_metrics.keys(), brow_metrics.values()
):
    with bcol:
        st.metric(label=metric, value=round(score, 3))

# subset metrics
crow_metrics = {k: metrics[k] for k in list_values_secondary}

ccol1, ccol2, ccol3, ccol4 = st.columns(4)
for ccol, metric, score in zip(
    (ccol1, ccol2, ccol3, ccol4), crow_metrics.keys(), crow_metrics.values()
):
    with ccol:
        st.metric(label=metric, value=round(score, 3))

# subset metrics
drow_metrics = {k: metrics[k] for k in list_values_tertiary}

dcol1, dcol2 = st.columns(2)
for dcol, metric, score in zip(
    (dcol1, dcol2), drow_metrics.keys(), drow_metrics.values()
):
    with dcol:
        st.metric(label=metric, value=round(score, 3))


# https://github.com/dimboump/confusion-matrix-viz-calc/blob/main/app.py
def plot_cm(
    cm: np.ndarray,
    *,
    title: Optional[str] = None,
    # display_labels: List[str] = None,
    cmap: str = "Blues",
) -> None:
    #if display_labels is None:
    #    display_labels = ["0", "1"]

    fig, ax = plt.subplots()
    disp = ConfusionMatrixDisplay(cm, display_labels=None)
    disp.plot(cmap=cmap, ax=ax)
    ax.set_title(title)
    st.pyplot(fig)


plot_cm(
    cm_df,
    title="Confusion Matrix",
    cmap=cmap,
)

page_default_rounding = 3


st.header("Brief Explanation of Terms")
st.write("We consider the terms True and False to refer to the existence of a gun event. In contrast, we consider the terms Positive and Negative to refer to the existence of a Shotspotter alert.")

# matrix terms
st.subheader("True Negative (TN)")
st.write("We have a non-gun event together with a Shotspotter non-alert.")
st.write("TN =", binary_classification_counts_dict["True Negative"])

st.subheader("False Positive (FP)")
st.write("We have a non-gun event together with a Shotspotter alert.")
st.write("FP =", binary_classification_counts_dict["False Positive"])

st.subheader("False Negative (FN)")
st.write("We have a gun event together with a Shotspotter non-alert.")
st.write("FN =", binary_classification_counts_dict["False Negative"])

st.subheader("True Positive (TP)")
st.write("We have a gun event together with a Shotspotter alert.")
st.write("TP =", binary_classification_counts_dict["True Positive"])


st.header("Metrics")

st.subheader("Accuracy")
st.markdown("**Accuracy:** Overall how often is Shotspotter correct?")
st.write("Accuracy = (TP + TN) / (TP + FP + FN + TN)")
st.write("Accuracy =", metrics["Accuracy String"])
st.write("Accuracy =", metrics["Accuracy String 2"])
st.write("Accuracy =", round(metrics["Accuracy"], page_default_rounding))

st.subheader("Precision")
st.markdown("**Precision:** When there is a Shotspotter alert, how often is it correct?")
st.write("Precision = TP / (FP + TP)")
st.write("Precision =", metrics["Precision String"])
st.write("Precision =", metrics["Precision String 2"])
st.write("Precision =", round(metrics["Precision"], page_default_rounding))

st.subheader("Recall (Sensitivity, True Positive Rate)")
st.markdown("**Recall:** When there is a gun event, how often do we get a Shotspotter alert?")
st.write("Recall = TP / (TP + FN)")
st.write("Recall =", metrics["Recall String"])
st.write("Recall =", metrics["Recall String 2"])
st.write("Recall =", round(metrics["Recall"], page_default_rounding))

st.write("We see the recall metric of ", round(metrics["Recall"], page_default_rounding), f"equals {metrics["Recall"]:.0%}.")
st.write(f"We can regard this as {metrics["Recall"]:.0%} of gun events (or gun shootings) with a Shotspotter alert. This value is clearly {'lower than' if metrics["Recall"] < 0.9 else 'higher than' if metrics["Recall"] > 0.9 else 'equal to'} the 90% percent of shootings with a Shotspotter alert as mentioned in the barchart from the following webpage: [ShotSpotter Routinely Missed Reported Shootings, City Data Shows – South Side Weekly](https://southsideweekly.com/shotspotter-routinely-missed-reported-shootings-city-data-shows/).")

st.subheader("F1")
st.markdown("**F1:** is the weighted mean of the precision and recall")
st.write("F1 = 2 * (precision * recall) / (precision + recall)")
st.write("F1 = 2 * TP / (2 * TP + FP + FN)")
st.write("F1 =", metrics["F1 String"])
st.write("F1 =", metrics["F1 String 2"])
st.write("F1 =", round(metrics["F1"], page_default_rounding))

st.subheader("Specificity (True Negative Rate)")
st.markdown("**Specificity:** When there is a non-gun event, how often does Shotspotter give a non-alert?")
st.write("Specificity = TN / (TN + FP)")
st.write("Specificity =", metrics["Specificity String"])
st.write("Specificity =", metrics["Specificity String 2"])
st.write("Specificity =", round(metrics["Specificity"], page_default_rounding))

st.subheader("Negative Predictive Rate")
st.markdown("**Negative Predictive Rate:** When there is a Shotspotter non-alert, how often is there a non-gun event?")
st.write("Negative Predictive Rate = TN / (TN + FN)")
st.write("Negative Predictive Rate =", metrics["Negative Predictive Rate String"])
st.write("Negative Predictive Rate =", metrics["Negative Predictive Rate String 2"])
st.write("Negative Predictive Rate =", round(metrics["Negative Predictive Rate"], page_default_rounding))

st.subheader("False Positive Rate (Type-I error, False Alarm Rate)")
st.markdown("**False Positive Rate:** When there is a non-gun event, how often does Shotspotter give an alert?")
st.write("False Positive Rate = FP / (FP + TN)")
st.write("False Positive Rate =", metrics["False Positive Rate String"])
st.write("False Positive Rate =", metrics["False Positive Rate String 2"])
st.write("False Positive Rate =", round(metrics["False Positive Rate"], page_default_rounding))


st.subheader("False Discovery Rate")
st.markdown("**False Discovery Rate:** When there is a Shotspotter alert, how often is there a non-gun event?")
st.write("False Discovery Rate = FP / (FP + TP)")
st.write("False Discovery Rate =", metrics["False Discovery Rate String"])
st.write("False Discovery Rate =", metrics["False Discovery Rate String 2"])
st.write("False Discovery Rate =", round(metrics["False Discovery Rate"], page_default_rounding))

st.subheader("False Negative Rate (Type-II error)")
st.markdown("**False Negative Rate:** When there is a gun event, how often do we not get a Shotspotter non-alert?")
st.write("False Negative Rate =  FN / (FN + TP)")
st.write("False Negative Rate =", metrics["False Negative Rate String"])
st.write("False Negative Rate =", metrics["False Negative Rate String 2"])
st.write("False Negative Rate =", round(metrics["False Negative Rate"], page_default_rounding))


st.subheader("False Omission Rate")
st.markdown("**False Omission Rate:** When there is a Shotspotter non-alert, how often is there a gun event?")
st.write("False Omission Rate =  FN / (FN + TN)")
st.write("False Omission Rate =", metrics["False Omission Rate String"])
st.write("False Omission Rate =", metrics["False Omission Rate String 2"])
st.write("False Omission Rate =", round(metrics["False Omission Rate"], page_default_rounding))


# help text
st.markdown(
    "More more regarding the definitions of the terms used on this page please see the [Simple guide to confusion matrix terminology](https://www.dataschool.io/simple-guide-to-confusion-matrix-terminology/)."
)
