import datetime
from bokeh.server.server import Server
from tornado.ioloop import IOLoop
from bokeh.document import Document
from bokeh.models import (
    ColumnDataSource,
    RadioButtonGroup,
    Div,
    Button,
    DataTable,
    TableColumn,
)
from bokeh.layouts import layout, column, row
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

    def render_cards_radio_button_group(self, index: int, active: int):
        def radio_botton_group_on_change(attr: str, old_active: int, new_active: int):
            self.trade_config.update_cards()

        radio_button_group = RadioButtonGroup(labels=self.cards_labels, active=active)
        radio_button_group.on_change("active", radio_botton_group_on_change)

        div = Div(text=f"Card {index:02}")
        return layout([[div, radio_button_group]])

    def render(self):
        self.trade_config.cards._chosen_cards
        self.cards_radio_button_groups = []
        num = self.trade_config.cards.get_chosen_cards_num()
        for i in range(0, 20):
            active = 0
            if i < num:
                active = self.trade_config.cards._chosen_cards[i]
            self.cards_radio_button_groups.append(
                self.render_cards_radio_button_group(i + 1, active)
            )

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


class TheoUI:
    def __init__(self, config: TradeConfig):
        self.config = config
        self.field_name = [
            "Future theo",
            "150 Call theo",
            "130 Put theo",
            "150 Call delta",
            "130 Put delta",
        ]
        self.source = ColumnDataSource(
            data=dict(field_name=self.field_name, value=[None, None, None, None, None])
        )
        columns = [
            TableColumn(field="field_name", title="Field Name"),
            TableColumn(field="value", title="Value"),
        ]
        self.data_table = DataTable(
            source=self.source, columns=columns, index_position=None, header_row=False
        )

    def render(self):
        return self.data_table

    def update(self):
        new_data = dict(
            field_name=self.field_name,
            value=[
                self.config.future_theo,
                self.config.call_theo,
                self.config.put_theo,
                self.config.call_delta,
                self.config.put_delta,
            ],
        )
        self.source.data = new_data


class MainUI:
    def __init__(self, exchange: Exchange, config: TradeConfig):
        self.exchange = exchange
        self.config = config

    def ui_root(self, doc: Document):
        update_functions = []
        cardsUI = CardsUI(self.config)
        theoUI = TheoUI(self.config)
        update_functions.append(theoUI.update)

        doc.add_root(row(cardsUI.render(), theoUI.render()))

        def periodic_callbacks():
            for update_function in update_functions:
                update_function()

        doc.add_periodic_callback(periodic_callbacks, 500)


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
