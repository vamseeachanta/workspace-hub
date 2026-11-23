---
name: dash-6-authentication
description: 'Sub-skill of dash: 6. Authentication.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 6. Authentication

## 6. Authentication


**Basic Authentication:**
```python
from dash import Dash, html, dcc
import dash_auth

app = Dash(__name__)

# Basic authentication
VALID_USERNAME_PASSWORD_PAIRS = {
    "admin": "admin123",
    "user": "user123"
}

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

app.layout = html.Div([
    html.H1("Protected Dashboard"),
    html.P("You are authenticated!")
])

if __name__ == "__main__":
    app.run(debug=True)
```

**Custom Login (with session):**
```python
from dash import Dash, html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from flask import session

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.server.secret_key = "your-secret-key-here"

# Login form
login_form = dbc.Card([
    dbc.CardBody([
        html.H4("Login"),
        dbc.Input(id="username", placeholder="Username", className="mb-2"),
        dbc.Input(id="password", type="password", placeholder="Password", className="mb-2"),
        dbc.Button("Login", id="login-btn", color="primary"),
        html.Div(id="login-message")
    ])
], style={"maxWidth": "400px", "margin": "100px auto"})

# Main content
main_content = html.Div([
    html.H1("Dashboard"),
    html.P("Welcome! You are logged in."),
    dbc.Button("Logout", id="logout-btn", color="secondary")
])

app.layout = html.Div([
    dcc.Location(id="url"),
    html.Div(id="page-content")
])

@callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if session.get("authenticated"):
        return main_content
    return login_form

@callback(
    [Output("login-message", "children"),
     Output("url", "pathname")],
    Input("login-btn", "n_clicks"),
    [State("username", "value"),
     State("password", "value")],
    prevent_initial_call=True
)
def login(n_clicks, username, password):
    # Simple validation (use proper auth in production)
    if username == "admin" and password == "admin123":
        session["authenticated"] = True
        return "", "/"
    return dbc.Alert("Invalid credentials", color="danger"), "/"

@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("logout-btn", "n_clicks"),
    prevent_initial_call=True
)
def logout(n_clicks):
    session.clear()
    return "/"

if __name__ == "__main__":
    app.run(debug=True)
```
