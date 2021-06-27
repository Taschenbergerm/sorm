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
from dash.dependencies import Input, Output, State, MATCH, ALL
import flask
import dash_ace
from dash.exceptions import PreventUpdate
from flask import jsonify
from flask_cors import CORS
import json

from sorm_.sorm_ import Storage

server = flask.Flask(__name__)
CORS(server)
STORAGE = Storage("sqlite:////home/marvin/sorm.db")
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
        html.Div(id="delete-alert"),
        dcc.Store("snippet-id", storage_type="session", data=None),
        html.H2("Sorm", className="display-4"),
        html.Hr(),
        dbc.Button("Add", id="add", color="primary"),
        html.Hr(),
        html.P("Starred"),
        html.Div(id="starred"),
        html.Hr(),
        html.P("Languages"),
        html.Div(id="languages")
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div([dbc.FormGroup([
    dbc.InputGroup([
        dbc.InputGroupAddon("Snippet-Name", addon_type="prepend"),
    dbc.Input(id="name", placeholder="Name")]),
    dbc.ButtonGroup([
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
    dbc.Button("Save", id="save", color="success", className="mr-1"),
    dbc.Button("Delete", id="delete",color="danger", className="mr-1")]),
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
@app.callback(Output("delete", "disabled"),
              Input("snippet-id", "data"))
def toggle_delete(data):

    if data:
        return False
    else:
        return True



@app.callback(Output("editor", "mode"),
              Input("mode", "value"))
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
            dbc.Container(
                html.H5(
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
                [dbc.Row(dbc.Button(
                    row.name,
                    color="link",
                    id={"type": "snippet-name",
                        "index": row.id},
                    style={"margin-left": "1em", "color": "black"}))
                    for row  in snippets.itertuples()],
                id={"type": "group-collaps",
                    "index": id},
                is_open=False,
            ),
        ]
    )

@app.callback(Output("languages", "children"),
              Input("alerts", "children"),
              Input("delete-alert", "children"))
def fill_languages(created, deleted):
    language_mapping = STORAGE.query_languages()
    elements = []
    for id, language in language_mapping.items():
        snippets = STORAGE.query_available_snippets_by_id(id)
        card = make_item(id, language, snippets)
        elements.append(card)
    return html.Div(elements)


@app.callback(
    Output({"type": "group-collaps", "index": MATCH}, "is_open"),
    Input({"type": "group-toggle", "index": MATCH}, "n_clicks"),
    State({"type": "group-toggle", "index": MATCH}, "index"),
    State({"type": "group-collaps", "index": MATCH}, "is_open"),
)
def toggle_accordion(n_clicks, id,  state):
    return not state

@app.callback(
        Output("editor", "value"),
        Output("name", "value"),
        Output("snippet-id", "data"),
    [
        Input("add", "n_clicks"),
        Input({"type": "snippet-name", "index":ALL}, "n_clicks")],
    [
        State({"type": "snippet-name", "index":ALL}, "value")],
)
def add_snippet(add_clicks, n_clicks, val):
    triggered = [t["prop_id"] for t in dash.callback_context.triggered][0]
    if triggered == ".":
        raise PreventUpdate()
    elif triggered == "add.n_clicks":
        res = ("def foo(bar:str) -> str:\n    return 'bar'", "Placeholder", None)
    elif any(n_clicks) :
        d, _ = triggered.split(".")
        index = json.loads(d)
        snippet = STORAGE.query_snippet(index["index"])
        res = (snippet[0][0], snippet[0][1], snippet[0][2])
    else:
        raise PreventUpdate()
    return res


@app.callback(Output("delete-alert", "children"), Input("delete", "n_clicks"), State("snippet-id", "data"), State("name", "value"))
def delete_snippet(n_clicks, data, name):
    if n_clicks and data:
        STORAGE.delete(data)
        return dbc.Toast(
            f"Snippet {name} has been deleted",
            header=f"Deleted Snippet-{data}",
            is_open=True,
            dismissable=True,
            icon="danger",
            duration=1000,
            style={"position": "fixed", "top": 66, "right": 10, "width": 350})
               # top: 66 positions the toast below the navbar

    else:
        return html.Div()


@app.callback(
    Output("alerts", "children"),
    Input("save", "n_clicks"),
    State("mode", "value"),
    State("name", "value"),
    State("editor", "value"),
    State("snippet-id", "data")
)
def save_snippet(n_clicks, mode, name, snippet, snippet_id):
    if n_clicks and snippet_id:
        STORAGE.update(mode, name, snippet)
        return dbc.Toast(
            f"Snippet has been updated",
            header="Updated",
            is_open=True,
            dismissable=True,
            icon="success",
            duration=1000,
            style={"position": "fixed", "top": 66, "right": 10, "width": 350})
    elif n_clicks and not snippet_id:
        STORAGE.create(mode,name, snippet)
        return dbc.Toast(
            f"Snippet has been created",
            header="Created",
            is_open=True,
            dismissable=True,
            icon="success",
            duration=1000,
            style={"position": "fixed", "top": 66, "right": 10, "width": 350})
    else:
        return html.Div()



if __name__ == '__main__':
    app.run_server(debug=True)
