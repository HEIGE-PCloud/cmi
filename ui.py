import datetime
from bokeh.server.server import Server
from tornado.ioloop import IOLoop
from bokeh.document import Document
from bokeh.models import Div, RadioButtonGroup, Button
from bokeh.layouts import layout, row
from typing import Callable, List

from exchange import Exchange

IP_ADDRESS = "0.0.0.0"


callback_functions: List[Callable] = []

def periodic_callback():
    for func in callback_functions:
        func()

def render_cards_radio_button_group(index: int):
    cards_labels = ["Unknown", "A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

    def radio_botton_group_on_change(attr: str, old_active: int, new_active: int):
        print(new_active)

    radio_button_group = RadioButtonGroup(labels=cards_labels, active=0)
    radio_button_group.on_change('active', radio_botton_group_on_change)
    
    div = Div(text=f"Card {index:02}")
    return layout([[div, radio_button_group]])

def render_cards_selection():
    cards_radio_button_groups = [render_cards_radio_button_group(i) for i in range(1, 21)]
    
    def reset_all_button_handler():
        for radio_button_group in cards_radio_button_groups:
            radio_button_group.children[0].children[1].active = 0

    reset_all_button = Button(label="Reset all", button_type="danger")
    reset_all_button.on_event("button_click", reset_all_button_handler)

    # cards_radio_button_groups.append(reset_all_button)

    return layout([cards_radio_button_groups], reset_all_button)
        

def ui_root(doc: Document):
    global cmi
    div = Div(text=f"Current rank: {cmi.get_rank()} {datetime.datetime.now()}")
    cards_selection = render_cards_selection()
    
    doc.add_root(layout([div, cards_selection]))
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
    # server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()


if __name__ == "__main__":
    start_ui()
