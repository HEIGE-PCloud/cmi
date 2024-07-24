import datetime
from bokeh.server.server import Server
from tornado.ioloop import IOLoop
from bokeh.document import Document
from bokeh.models import Div
from bokeh.layouts import layout
from typing import Callable, List

from exchange import Exchange

IP_ADDRESS = "127.0.0.1"


callback_functions: List[Callable] = []

def periodic_callback():
    for func in callback_functions:
        func()



def ui_root(doc: Document):
    global cmi
    div = Div(text=f"Current rank: {cmi.get_rank()} {datetime.datetime.now()}")
    doc.add_root(layout([div]))
    doc.add_periodic_callback(periodic_callback, 1000)


def start_ui(exchange: Exchange):
    global cmi
    cmi = exchange
    server = Server(
        {"/": ui_root},
        num_procs=1,
        io_loop=IOLoop(),
        address=IP_ADDRESS,
        allow_websocket_origin=["*"],
    )
    server.start()
    print(f"Starting turbot ui on http://{IP_ADDRESS}:5006/")
    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()


if __name__ == "__main__":
    start_ui()
