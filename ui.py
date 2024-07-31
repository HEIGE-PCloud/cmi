import datetime
from bokeh.server.server import Server
from tornado.ioloop import IOLoop
from bokeh.document import Document
from bokeh.models import Div, RadioButtonGroup, Button, ColumnDataSource, DataTable, TableColumn
from bokeh.layouts import layout, row
from typing import Callable, List, Optional

from exchange import Exchange
from trade_config import TradeConfig

IP_ADDRESS = "127.0.0.1"


callback_functions: List[Callable] = []


def periodic_callback():
    for func in callback_functions:
        func()


def render_cards_radio_button_group(index: int):
    cards_labels = [
        "Unknown",
        "A",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "J",
        "Q",
        "K",
    ]

    def radio_botton_group_on_change(attr: str, old_active: int, new_active: int):
        global trade_config
        trade_config.update_cards()
        print(trade_config.cards.get_theoretical_price())

    radio_button_group = RadioButtonGroup(labels=cards_labels, active=0)
    radio_button_group.on_change("active", radio_botton_group_on_change)

    div = Div(text=f"Card {index:02}")
    return layout([[div, radio_button_group]])


def render_cards_selection():
    cards_radio_button_groups = [
        render_cards_radio_button_group(i) for i in range(1, 21)
    ]

    def reset_all_button_handler():
        for radio_button_group in cards_radio_button_groups:
            radio_button_group.children[0].children[1].active = 0

    def get_cards_value():
        res = []
        for radio_button_group in cards_radio_button_groups:
            val = radio_button_group.children[0].children[1].active
            if val != 0:
                res.append(val)
        return res

    reset_all_button = Button(label="Reset all", button_type="danger")
    reset_all_button.on_event("button_click", reset_all_button_handler)

    # cards_radio_button_groups.append(reset_all_button)

    return layout([cards_radio_button_groups], reset_all_button), get_cards_value


def build_simple_datasource():
    source = ColumnDataSource(data=dict(data=[]))

    def update():
        source.stream({"data": [datetime.datetime.now()]}, rollover=10)

    callback_functions.append(update)
    return source


def ui_root(doc: Document):
    global cmi
    source = build_simple_datasource()
    div = Div(text=f"Current rank: {cmi.get_rank()}")
    data_table = DataTable(source=source, columns=[TableColumn(field="data", title="Data")])
    cards_selection, get_cards_value = render_cards_selection()
    trade_config.get_cards_value = get_cards_value

    doc.add_root(layout([div, data_table, cards_selection]))

    doc.add_periodic_callback(periodic_callback, 500)


class UI():
    
    def __init__(self, exchange: Exchange, trade_config: TradeConfig) -> None:
        self.exchange = exchange
        self.trade_config = trade_config

def start_ui(exchange: Exchange, tc: TradeConfig):
    global cmi
    cmi = exchange
    global trade_config
    trade_config = tc
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


# if __name__ == "__main__":
#     start_ui()
