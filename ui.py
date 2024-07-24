from bokeh.server.server import Server
from tornado.ioloop import IOLoop
from bokeh.document import Document


def ui_root(doc: Document):
    pass


def start_ui():
    server = Server(
        {"/": ui_root},
        num_procs=1,
        io_loop=IOLoop(),
        address="127.0.0.1",
        allow_websocket_origin=["*"],
    )
    server.start()
    print("Starting turbot ui on http://0.0.0.0:5006/")
    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()


if __name__ == "__main__":
    start_ui()
