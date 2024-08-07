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
    NumberEditor,
)
from bokeh.layouts import layout, column, row


from exchange import Exchange
from trade_config import TradeConfig

IP_ADDRESS = "0.0.0.0"


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


class MonitorTable:
    def __init__(self, config: TradeConfig):
        self.config = config
        self.field_name = [
            "Rank",
            "Cards theo",
            "Future ask",
            "Future theo",
            "Future bid",
            "Call ask",
            "Call theo",
            "Call bid",
            "Put ask",
            "Put theo",
            "Put bid",
            "Call delta",
            "Put delta",
            "Total delta"
        ]
        self.source = ColumnDataSource(
            data=dict(field_name=self.field_name, value=[None] * len(self.field_name))
        )
        columns = [
            TableColumn(field="field_name", title="Field Name"),
            TableColumn(field="value", title="Value"),
        ]
        self.data_table = DataTable(
            source=self.source,
            columns=columns,
            index_position=None,
            header_row=False,
            height=25 * len(self.field_name)
        )

    def render(self):
        return self.data_table

    def update(self):
        new_data = dict(
            field_name=self.field_name,
            value=[
                self.config.exchange.get_rank(),
                self.config.cards.get_theoretical_price(),
                self.config.future.ask_price,
                self.config.future.theo_price,
                self.config.future.bid_price,
                self.config.call.ask_price,
                self.config.call.theo_price,
                self.config.call.bid_price,
                self.config.put.ask_price,
                self.config.put.theo_price,
                self.config.put.bid_price,
                self.config.pricer.call_delta,
                self.config.pricer.put_delta,
                self.config.hedge.compute_total_delta()
            ],
        )
        self.source.data = new_data


class ControlTable:
    def __init__(self, config: TradeConfig) -> None:
        self.config = config
        self.field_name = [
            "Future credit",
            "Call credit",
            "Put credit",
            "Hedge interval",
            "Future mm_interval",
            "Call mm_interval",
            "Put mm_interval",
        ]
        self.source = ColumnDataSource(
            data=dict(
                field_name=self.field_name,
                value=[
                    self.config.future.credit,
                    self.config.call.credit,
                    self.config.put.credit,
                    self.config.hedge.hedge_interval,
                    self.config.future.mm_interval,
                    self.config.call.mm_interval,
                    self.config.put.mm_interval,
                ],
            )
        )
        columns = [
            TableColumn(field="field_name", title="Field Name"),
            TableColumn(field="value", title="Value"),
        ]

        for col in columns:
            if col.field == "value":
                col.editor = NumberEditor()

        self.data_table = DataTable(
            source=self.source,
            columns=columns,
            editable=True,
            index_position=None,
            header_row=False,
            auto_edit=True
        )

        self.source.on_change("data", self.sync_config)

    def render(self):
        return self.data_table

    def sync_config(self, attr, old, new):
        for idx, field in enumerate(self.field_name):
            if field == "Future credit":
                self.config.future.credit = new["value"][idx]


class MainUI:
    def __init__(self, exchange: Exchange, config: TradeConfig):
        self.exchange = exchange
        self.config = config

    def ui_root(self, doc: Document):
        cardsUI = CardsUI(self.config)
        theoUI = MonitorTable(self.config)
        futureUI = ControlTable(self.config)
        update_functions = [theoUI.update]

        doc.add_root(row(cardsUI.render(), column(theoUI.render(), futureUI.render())))

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
