from views.data_visuals_view import make_layout
from maindash import app


if __name__ == '__main__':
    app.layout = make_layout()
    app.run_server(debug=True)
