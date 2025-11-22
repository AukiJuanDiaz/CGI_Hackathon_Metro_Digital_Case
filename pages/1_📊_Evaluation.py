import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.graph_objects as go
import matplotlib.colors as mcolors

st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed",
    page_title="ChatBot Evaluation Dashboard",
)

st.title("ChatBot Evaluation Dashboard")
st.write("Compare different versions of the Metro Bots!")

# ------------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------------

if "left_data" not in st.session_state:
    st.session_state.left_data = None

if "right_data" not in st.session_state:
    st.session_state.right_data = None

left, divider, right = st.columns([1, 0.02, 1])


available_bots = ["Meta-Llama-3.1-8B-Instruct + RAG v1.0", 
                  "Meta-Llama-3.1-8B-Instruct + RAG v1.1", 
                  "Meta-Llama-3.1-405B-Instruct-FP8 v1.0"]
available_eval_data = {
    "Meta-Llama-3.1-8B-Instruct + RAG v1.0": "evaldata/model_1_v1_0_merged.csv",
    "Meta-Llama-3.1-8B-Instruct + RAG v1.1": "evaldata/model_1_v1_1_merged.csv",
    "Meta-Llama-3.1-405B-Instruct-FP8 v1.0": "evaldata/model_2_v1_0_merged.csv"
}

metrics = ["Correctness", "Clarity", "Hospitality_Tonality", "Relevance", "Hallucination-Safety"]

metric_score_columns = {
    "Correctness": "Correctness_Score",
    "Clarity": "Clarity_Score",
    "Hospitality_Tonality": "Hospitality_Tonality_Score",
    "Relevance": "Relevance_Score",
    "Hallucination-Safety": "Hallucination_Score"
}

metric_reason_columns = {
    "Correctness": "Correctness_Reason",
    "Clarity": "Clarity_Reason",
    "Hospitality_Tonality": "Hospitality_Tonality_Reason",
    "Relevance": "Relevance_Reason",
    "Hallucination-Safety": "Hallucination_Reason"
}

categories = ["Synonym", "Scenario", "Syntax", "Implicit Question", "Tricky Questions"]

categories_synonyms = {
    "Synonym": "synonym",
    "Scenario": "scenario",
    "Syntax": "fehler",
    "Implicit Question": "keinFrage",
    "Tricky Questions": "trick"
}

left_color = "#e79174"
right_color = "#64d9c8"


# ------------------------------------------------------------------
# >>> NEW CATEGORY FUNCTIONS <<<
# ------------------------------------------------------------------

def normalize_categories(df, categories_synonyms):
    reverse_mapping = {v.lower(): v for v in categories_synonyms.values()}

    df = df.copy()
    df["type change"] = (
        df["type change"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map(reverse_mapping)
    )
    return df


def compute_category_metrics(df, metric_score_columns):
    category_metrics = {}

    for metric, col in metric_score_columns.items():
        category_avg = df.groupby("type change")[col].mean()
        category_metrics[metric] = category_avg

    # Return shape: metrics × categories
    return pd.DataFrame(category_metrics).T


def prepare_heatmap_data(metrics_df, categories_synonyms, metrics):
    categories = list(categories_synonyms.values())

    metrics_df = metrics_df.reindex(index=metrics, columns=categories)
    values = metrics_df.values
    return values, categories, metrics


# ------------------------------------------------------------------
# Appearance helpers
# ------------------------------------------------------------------

def generate_smooth_gradient(base_color, n=100):
    base_rgb = np.array(mcolors.to_rgb(base_color))
    t = np.linspace(0, 1, n)

    colors = []
    for ti in t:
        if ti < 0.5:
            alpha = 2 * ti
            rgb = (1 - alpha) * np.ones(3) + alpha * base_rgb
        else:
            alpha = 2 * (ti - 0.5)
            rgb = (1 - alpha) * base_rgb
        colors.append(mcolors.to_hex(rgb))
    return colors

with divider:
    st.markdown(
        "<div style='border-left: 2px solid #ccc; height: 100vh; margin: auto;'></div>",
        unsafe_allow_html=True
    )


# ------------------------------------------------------------------
# CHART RENDERING
# ------------------------------------------------------------------

def render_chart(df, title, bar_color):
    chart = (
        alt.Chart(df)
        .mark_bar(color=bar_color)
        .encode(
            y=alt.Y("labels:N", sort=None, title="Metric"),
            x=alt.X("values:Q", scale=alt.Scale(domain=[0, 5]), title="Score"),
            tooltip=["labels", "values"]
        )
        .properties(width="container", height=600, title=title)
    )
    st.altair_chart(chart, use_container_width=True)


# ------------------------------------------------------------------
# DATA HELPERS
# ------------------------------------------------------------------

def load_dataframe(model_file: str) -> pd.DataFrame:
    return pd.read_csv(model_file)

def compute_average_metrics(df: pd.DataFrame) -> pd.DataFrame:
    averages = {m: round(df[col].mean(), 2) for m, col in metric_score_columns.items()}
    return pd.DataFrame({"labels": list(averages.keys()), "values": list(averages.values())})

def compute_worst_questions(df: pd.DataFrame, metric: str, n: int = 3) -> pd.DataFrame:
    col_score = metric_score_columns[metric]
    col_reason = metric_reason_columns[metric]

    worst = df.nsmallest(n, col_score)[[col_score, "Question", "Actual_Answer", col_reason, "FAQ answers"]]
    worst = worst.rename(columns={col_score: "Score", col_reason: "Judgement"})

    return worst


# ------------------------------------------------------------------
# LEFT PANEL
# ------------------------------------------------------------------

with left:
    st.subheader("Chatbot 1")

    option_left = st.selectbox("Select a ChatBot to evaluate:", available_bots, key="left_select")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Run Evaluation", key="run_left", disabled=True):
            st.session_state.left_data = pd.DataFrame({
                "labels": metrics,
                "values": np.round(1 + 4 * np.random.rand(len(metrics)), 2)
            })
    
    with col2:
        if st.button("Load Evaluation Data", key="load_left"):
            df = load_dataframe(available_eval_data[option_left])
            df = normalize_categories(df, categories_synonyms)
            st.session_state.left_df = df
            st.session_state.left_data = compute_average_metrics(df)

    if st.session_state.left_data is not None:
        render_chart(st.session_state.left_data, "Evaluation Result", left_color)

        with st.expander("Show Detail Analysis"):

            # -----------------------------
            # >>> real heatmap data here
            # -----------------------------
            metrics_df = compute_category_metrics(st.session_state.left_df, metric_score_columns)
            values, categories_used, metrics_used = prepare_heatmap_data(
                metrics_df, categories_synonyms, metrics
            )

            heatmap_data = pd.DataFrame(values, index=metrics_used, columns=categories_used)
            heatmap_data = heatmap_data.reset_index().melt(id_vars="index")
            heatmap_data.columns = ["Metric", "Category", "Value"]

            gradient_left = generate_smooth_gradient(left_color, n=100)[::-1]

            # Map category names back to display names
            category_display_names = {v: k for k, v in categories_synonyms.items()}
            heatmap_data["Category"] = heatmap_data["Category"].map(category_display_names)
            
            heatmap_left = alt.Chart(heatmap_data).mark_rect(
                stroke='black', strokeWidth=1
            ).encode(
                x=alt.X("Category:N", title="Category", sort=list(category_display_names.values()), axis=alt.Axis(labelAngle=-45)),
                y=alt.Y("Metric:N", title="Metric", sort=metrics_used),
                color=alt.Color("Value:Q",
                                scale=alt.Scale(domain=[1, 5], range=gradient_left),
                                legend=alt.Legend(orient="top")),
                tooltip=["Metric", "Category", "Value"]
            ).properties(width=400, height=400, title="Category Analysis Heatmap")

            st.altair_chart(heatmap_left, use_container_width=True)

        with st.expander("Show worst performing questions"):
            detail_metric_left = st.selectbox(
                "Select Metric for Detailed View:",
                metrics,
                key="detail_metric_left"
            )

            # Retrieve the worst performing questions for the metric
            # I need to rename to columns from the df before calling the function
            # Rename columns in the dataframe before computing worst questions
            df_renamed = st.session_state.left_df.rename(columns={
                "modifiert question": "Question",
                "answer_chatbot": "Actual_Answer"
            })

            left_worst_questions_df = compute_worst_questions(df_renamed, detail_metric_left, 3)

            st.dataframe(left_worst_questions_df, hide_index=True, use_container_width=True)


# ------------------------------------------------------------------
# RIGHT PANEL
# ------------------------------------------------------------------

with right:
    st.subheader("Chatbot 2")

    option_right = st.selectbox("Select a ChatBot to evaluate:", available_bots, key="right_select")



    col1, col2 = st.columns(2)
    with col1:
        if st.button("Run Evaluation", key="run_right", disabled=True):
            st.session_state.right_data = pd.DataFrame({
                "labels": metrics,
                "values": np.round(1 + 4 * np.random.rand(len(metrics)), 2)
            })
    
    with col2:
        if st.button("Load Evaluation Data", key="load_right"):
            df = load_dataframe(available_eval_data[option_right])
            df = normalize_categories(df, categories_synonyms)
            st.session_state.right_df = df
            st.session_state.right_data = compute_average_metrics(df)


    if st.session_state.right_data is not None:
        render_chart(st.session_state.right_data, "Evaluation Result", right_color)

        with st.expander("Show Detail Analysis"):

            # -----------------------------
            # >>> real heatmap data here
            # -----------------------------
            metrics_df = compute_category_metrics(st.session_state.right_df, metric_score_columns)
            values, categories_used, metrics_used = prepare_heatmap_data(
                metrics_df, categories_synonyms, metrics
            )

            heatmap_data = pd.DataFrame(values, index=metrics_used, columns=categories_used)
            heatmap_data = heatmap_data.reset_index().melt(id_vars="index")
            heatmap_data.columns = ["Metric", "Category", "Value"]

            gradient_right = generate_smooth_gradient(right_color, n=100)[::-1]
            # Map category names back to display names
            category_display_names = {v: k for k, v in categories_synonyms.items()}
            heatmap_data["Category"] = heatmap_data["Category"].map(category_display_names)
            
            heatmap_right = alt.Chart(heatmap_data).mark_rect(
                stroke='black', strokeWidth=1
            ).encode(
                x=alt.X("Category:N", title="Category", sort=list(category_display_names.values()),
                        axis=alt.Axis(labelAngle=-45)),
                y=alt.Y("Metric:N", title="Metric", sort=metrics_used),
                color=alt.Color("Value:Q",
                                scale=alt.Scale(domain=[1, 5], range=gradient_right),
                                legend=alt.Legend(orient="top")),
                tooltip=["Metric", "Category", "Value"]
            ).properties(width=400, height=400, title="Category Analysis Heatmap")

            st.altair_chart(heatmap_right, use_container_width=True)

        with st.expander("Show worst performing questions"):
            detail_metric_right = st.selectbox(
                "Select Metric for Detailed View:",
                metrics,
                key="detail_metric_right"
            )

            # Retrieve the worst performing questions for the metric
            # I need to rename to columns from the df before calling the function
            # Rename columns in the dataframe before computing worst questions
            df_renamed = st.session_state.right_df.rename(columns={
                "modifiert question": "Question",
                "answer_chatbot": "Actual_Answer"
            })

            right_worst_questions_df = compute_worst_questions(df_renamed, detail_metric_right, 3)

            st.dataframe(right_worst_questions_df, hide_index=True, use_container_width=True)


# ------------------------------------------------------------------
# SPIDER CHART (unchanged)
# ------------------------------------------------------------------

def hex_to_rgba(hex_color: str, alpha: float = 0.2) -> str:
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join(2 * c for c in hex_color)
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


if st.session_state.left_data is not None and st.session_state.right_data is not None:
    st.subheader("Comparison Spider Chart")

    def make_spider_chart(left_df, right_df, left_label, right_label, left_color, right_color):
        categories = left_df['labels'].tolist()
        left_values = left_df['values'].tolist()
        right_values = right_df['values'].tolist()

        fill_alpha = 0.3
        left_fill = hex_to_rgba(left_color, fill_alpha)
        right_fill = hex_to_rgba(right_color, fill_alpha)

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=left_values, theta=categories, fill='toself',
            name=left_label, line=dict(color=left_color), fillcolor=left_fill
        ))

        fig.add_trace(go.Scatterpolar(
            r=right_values, theta=categories, fill='toself',
            name=right_label, line=dict(color=right_color), fillcolor=right_fill
        ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            showlegend=True,
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

    make_spider_chart(
        st.session_state.left_data,
        st.session_state.right_data,
        option_left,
        option_right,
        left_color=left_color,
        right_color=right_color
    )
