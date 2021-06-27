"""
This app creates a simple sidebar layout using inline style arguments and the
dbc.Nav component.

dcc.Location is used to track the current location, and a callback uses the
current location to render the appropriate page content. The active prop of
each NavLink is set automatically according to the current pathname. To use
this feature you must install dash-bootstrap-components >= 0.11.0.

For more details on building multi-page Dash applications, check out the Dash
documentation: https://dash.plot.ly/urls
"""
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH
import flask
import dash_ace
from flask import jsonify
from flask_cors import CORS

from sorm_.sorm_ import Storage

server = flask.Flask(__name__)
CORS(server)
Storage = Storage("sqlite:////home/marvin/sorm.db")
app = dash.Dash(__name__,
                server=server,
                external_stylesheets=[dbc.themes.BOOTSTRAP])

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.Div(id="alerts"),
        html.H2("Sorm", className="display-4"),
        html.Hr(),
        dbc.Button("Add", id="add"),
        html.Hr(),
        html.P("Starred"),
        html.Div(id="starred"),
        html.Hr(),
        html.P("Languages"),
        html.Div(id="languages"),
        html.P(
            "A simple sidebar layout with navigation links", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Page 1", href="/page-1", active="exact"),
                dbc.NavLink("Page 2", href="/page-2", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div([dbc.FormGroup([
    dbc.Input(id="name", placeholder="Name"),
    dbc.Select(
        id="mode",
        value="Python",
        options=[
            {"label": "Python", "value": "python"},
            {"label": "SQL", "value": "sql"},
            {"label": "Text", "value": "text"},
            {"label": "Norm", "value": "norm"},
        ],
    ),

    dbc.Button("Save", id="save")
], inline=True),
    dash_ace.DashAceEditor(
        id='editor',
        value='def test(a: int) -> str : \n'
              '    return f"value is {a}"',
        theme='github',
        mode='python',
        tabSize=2,
        enableBasicAutocompletion=True,
        enableLiveAutocompletion=True,
        autocompleter='/autocompleter?prefix=',
        placeholder='Python code ...'
    )],
    id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

@app.callback(Output("editor", "mode"), Input("mode", "value"))
def update_mode(val):
    return val


@app.callback(
    Output("starred", "children"),
    Input("alerts", "children")
)
def fill_starred(_):
    return html.Div()


def make_item(id, name, snippets):
    # we use this function to make the example items to avoid code duplication
    return dbc.Card(
        [
            dbc.CardHeader(
                html.H2(
                    dbc.Button(
                        name,
                        color="link",
                        id={"type": "group-toggle",
                            "index": id},
                        n_clicks=0,
                    )
                )
            ),
            dbc.Collapse(
                [dbc.Button(
                    row["name"],
                    id={"type": "snipped-name",
                        "index": row["id"]})
                 for row  in snippets.itertuples()],
                id={"type": "group-collaps",
                    "index": id},
                is_open=False,
            ),
        ]
    )

@app.callback(Output("languages", "children"), Input("alerts", "children"))
def fill_languages(_):
    language_mapping = Storage.query_languages()
    snippets = Storage.query_available_snippets()
    elements = []
    for id, language in language_mapping.items():
        card = make_item(id, language, snippets.query(f"language == {id}"))
        elements.extend(card)
    return html.Div(elements)


@app.callback(
    Output({"type": "group-collaps", "index": MATCH}, "is_open"),
    Input({"type": "group-toggle", "index": MATCH}, "n_clicks"),
    State({"type": "group-toggle", "index": MATCH}, "index"),
    State({"type": "group-collaps", "index": MATCH}, "is_open"),
)
def toggle_accordion(n_clicks, id,  state):
    print(f"Match triggered from {id} with {n_clicks} and current state is {state}")
    return not state

@app.callback(

    Output("editor", "value"),
    Input("add", "n_clicks")
)
def add_snipped(_):
    print("Button hit ")
    return ""

@app.callback(
    Output("alerts", "children"),
    Input("save", "n_clicks"),
    State("mode", "value"),
    State("name", "value"),
    State("editor", "value")
)
def save_snipped(_, mode, name, snippet):
    code_snippet = (mode, name, snippet)
    print(code_snippet)
    return html.Div()


if __name__ == '__main__':
    app.run_server(debug=True)
