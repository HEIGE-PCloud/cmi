import datetime
from bokeh.server.server import Server
from tornado.ioloop import IOLoop
from bokeh.document import Document
from bokeh.models import ColumnDataSource, RadioButtonGroup, Div, Button
from bokeh.layouts import layout
from bokeh.plotting import figure
import numpy as np

from typing import Callable, List, Optional

from exchange import Exchange
from trade_config import TradeConfig

IP_ADDRESS = "127.0.0.1"


class CardsUI:

    def __init__(self, trade_config: TradeConfig):
        self.trade_config = trade_config
        self.trade_config.get_cards_value = self.get_cards_value
        self.cards_radio_button_groups = []
        self.cards_labels = [
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

    def render_cards_radio_button_group(self, index: int):
        def radio_botton_group_on_change(attr: str, old_active: int, new_active: int):
            self.trade_config.update_cards()
            print(self.trade_config.cards.get_theoretical_price())

        radio_button_group = RadioButtonGroup(labels=self.cards_labels, active=0)
        radio_button_group.on_change("active", radio_botton_group_on_change)

        div = Div(text=f"Card {index:02}")
        return layout([[div, radio_button_group]])

    def render(self):
        self.cards_radio_button_groups = [
            self.render_cards_radio_button_group(i) for i in range(1, 21)
        ]

        def reset_all_button_handler():
            for radio_button_group in self.cards_radio_button_groups:
                radio_button_group.children[0].children[1].active = 0

        reset_all_button = Button(label="Reset all", button_type="danger")
        reset_all_button.on_event("button_click", reset_all_button_handler)
        return layout([self.cards_radio_button_groups], reset_all_button)

    def get_cards_value(self):
        res = []
        for radio_button_group in self.cards_radio_button_groups:
            val = radio_button_group.children[0].children[1].active
            if val != 0:
                res.append(val)
        return res


class MainUI:
    def __init__(self, exchange: Exchange, config: TradeConfig):
        self.exchange = exchange
        self.config = config

    def ui_root(self, doc: Document):
        update_functions = []
        c = CardsUI(self.config)
        source = ColumnDataSource(data=dict(x=[], y=[]))
        p = figure(title="Random Data Plot", x_axis_label="x", y_axis_label="y")
        p.line("x", "y", source=source, line_width=2)
        doc.add_root(layout([p, c.render()]))

        def update():
            new_data = dict(x=[np.random.random()], y=[np.random.random()])
            source.stream(new_data, rollover=100)

        update_functions.append(update)

        def periodic_callbacks():
            for update_function in update_functions:
                update_function()

        doc.add_periodic_callback(periodic_callbacks, 1000)


def start_ui(exchange: Exchange, trade_config: TradeConfig):
    ui = MainUI(exchange, trade_config)
    server = Server(
        {"/": ui.ui_root},
        num_procs=1,
        io_loop=IOLoop(),
        address=IP_ADDRESS,
        allow_websocket_origin=["*"],
    )
    server.start()
    print(f"Starting turbot ui on http://{IP_ADDRESS}:5006/")
    server.io_loop.start()


if __name__ == "__main__":
    start_ui(None, TradeConfig())
