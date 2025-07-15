from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import webbrowser
import threading

# Load and prepare data
df = pd.read_csv("cost_data.csv", delimiter="\t")
df.columns = df.columns.str.strip()
df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

app = Dash(__name__)

app.layout = html.Div([
    html.H2("Cost Estimator by Model & Provider -— Timeline Generative Posts ", style={"textAlign": "center"}),

    html.Div([

          html.Div([
            html.Label("Prompt length (# words)", style={"marginRight": "10px"}),
            dcc.Input(
                id="prompt-length",
                type="number",
                value=750,
                min=0,
                step=1,
                debounce=True,
                style={"width": "120px"}
            ),
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "15px"}),
        
        html.Div([
            html.Label("Transaction history size (# chars):", style={"marginRight": "10px"}),
            dcc.Input(
                id="input-words",
                type="number",
                value=750,
                min=0,
                step=1,
                debounce=True,
                style={"width": "120px"}
            ),
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "15px"}),

        html.Div([
            html.Label("Output Length (words):", style={"marginRight": "10px"}),
            dcc.Input(
                id="output-words",
                type="number",
                value=150,
                min=0,
                step=1,
                debounce=True,
                style={"width": "120px"}
            ),
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "15px"}),

        html.Div([
            html.Label("Number of Runs:", style={"marginRight": "10px"}),
            dcc.Input(
                id="runs",
                type="number",
                value=1,
                min=1,
                step=1,
                debounce=True,
                style={"width": "120px"}
            ),
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "15px"}),

        html.Div([
            html.Label("Number of Customers:", style={"marginRight": "10px"}),
            dcc.Input(
                id="customers",
                type="number",
                value=1,
                min=1,
                step=1,
                debounce=True,
                style={"width": "120px"}
            ),
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "15px"}),

        
        html.Div([
            html.Label("Currency:", style={"marginRight": "10px"}),
            dcc.Dropdown(
                id="currency",
                options=[
                    {"label": "USD ($)", "value": "USD"},
                    {"label": "ZAR (R)", "value": "ZAR"}
                ],
                value="USD",
                clearable=False,
                style={"width": "150px"}
            )
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "15px"}),

        html.Div([
            html.Label("Select Providers:"),
            dcc.Checklist(
                id="provider-checklist",
                options=[{"label": p, "value": p} for p in df["provider"].unique()],
                value=list(df["provider"].unique()),
                inline=True,
                inputStyle={"marginRight": "5px", "marginLeft": "10px"}
            )
        ], style={"marginTop": "20px"})
    ], style={"maxWidth": "500px", "margin": "auto", "padding": "20px"}),

    html.Hr(),

    dcc.Graph(id="cost-graph")
], style={"fontFamily": "Arial, sans-serif", "backgroundColor": "#fafafa", "padding": "20px"})


@app.callback(
    Output("cost-graph", "figure"),
    Input("provider-checklist", "value"),
    Input("prompt-length", "value"),
    Input("input-words", "value"),
    Input("output-words", "value"),
    Input("runs", "value"),
    Input("customers", "value"),
    Input("currency", "value")
)

def update_cost_chart(selected_providers, prompt_length, input_words, output_words, runs, customers, currency):

    input_words = input_words or 0
    output_words = output_words or 0
    runs = runs or 1
    customers = customers or 1

    total_runs = runs * customers

    word_to_token = 1.33
    prompt_tokens = prompt_length * word_to_token

    char_to_token = 0.25
    input_tokens = input_words * word_to_token
    
    output_tokens = output_words * word_to_token

    total_inputs = input_tokens + prompt_tokens
    
    filtered_df = df[df["provider"].isin(selected_providers)].copy()

    total_cost_usd = total_runs * (
        (total_inputs * filtered_df["input_cost_per_1k"] / 1000) +
        (output_tokens * filtered_df["output_cost_per_1k"] / 1000)
    )

    if currency == "ZAR":
        filtered_df["total_cost"] = total_cost_usd * USD_TO_ZAR
        y_label = "ZAR (R)"
    else:
        filtered_df["total_cost"] = total_cost_usd
        y_label = "USD ($)"

    filtered_df["label"] = filtered_df["provider"] + " - " + filtered_df["model"]

    fig = px.bar(
        filtered_df,
        x="label",
        y="total_cost",
        color="provider",
        title=f"Total Cost ({input_words} input words, {output_words} output words) in {y_label}",
        labels={"total_cost": y_label, "label": "Model"},
        text_auto=".4f"
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff"
    )

    return fig

# def open_browser():
#     webbrowser.open_new_tab("http://127.0.0.1:8050/")
   
# threading.Timer(1, open_browser).start()
app.run(debug=False, use_reloader=False)