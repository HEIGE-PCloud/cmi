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
from trade_config import ManualNewsState, TradeConfig
import logging

logger = logging.getLogger(__name__)
IP_ADDRESS = "0.0.0.0"


class ManualNewsTradeControlUI:
    def __init__(self, config: TradeConfig) -> None:
        self.config = config
        self.labels = ["PAUSE", "TRADE", "HEDGE"]

        def handle(attr: str, old_active: int, new_active: int):
            self.config.manul_news_state = ManualNewsState(new_active)

        self.radio_button_group = RadioButtonGroup(
            labels=self.labels, active=config.manul_news_state.value
        )
        self.radio_button_group.on_change("active", handle)

    def render(self):
        return self.radio_button_group
    
    def set_trade(self):
        logger.info("set_trade")
        self.radio_button_group.active = ManualNewsState.TRADE.value
        self.config.manul_news_state = ManualNewsState.TRADE


class CardsUI:

    def __init__(self, trade_config: TradeConfig, control_UI: ManualNewsTradeControlUI):
        self.trade_config = trade_config
        self.control_UI = control_UI
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
            self.control_UI.set_trade()

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
            "Mode",
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
            "Total delta",
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
            height=25 * len(self.field_name),
        )

    def render(self):
        return self.data_table

    def update(self):
        new_data = dict(
            field_name=self.field_name,
            value=[
                self.config.mode.name,
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
                self.config.hedger.compute_total_delta(),
            ],
        )
        self.source.data = new_data


class ControlTable:
    def __init__(self, config: TradeConfig) -> None:
        self.config = config
        self.field_name = [
            "Thread count",
            "Iteration count",
            "Hedger credit",
            "Future credit",
            "Call credit",
            "Put credit",
            "Hedge interval",
            "Future interval",
            "Call interval",
            "Put interval",
        ]
        self.source = ColumnDataSource(
            data=dict(
                field_name=self.field_name,
                value=[
                    self.config.pricer.thread_count,
                    self.config.pricer.iteration_count,
                    self.config.hedger.credit,
                    self.config.future.credit,
                    self.config.call.credit,
                    self.config.put.credit,
                    self.config.hedger.hedge_interval,
                    self.config.future.interval,
                    self.config.call.interval,
                    self.config.put.interval,
                ],
            )
        )
        field_name_column = TableColumn(field="field_name", title="Field Name")
        value_column = TableColumn(field="value", title="Value")
        value_column.editor = NumberEditor()

        columns = [
            field_name_column,
            value_column,
        ]

        self.data_table = DataTable(
            source=self.source,
            columns=columns,
            editable=True,
            index_position=None,
            header_row=False,
        )

        self.source.on_change("data", self.sync_config)

    def render(self):
        return self.data_table

    def sync_config(self, attr, old, new):
        for idx, field in enumerate(self.field_name):
            match field:
                case "Thread count":
                    self.config.pricer.thread_count = new["value"][idx]
                case "Iteration count":
                    self.config.pricer.iteration_count = new["value"][idx]
                case "Hedger credit":
                    self.config.hedger.credit = new["value"][idx]
                case "Future credit":
                    self.config.future.credit = new["value"][idx]
                case "Call credit":
                    self.config.call.credit = new["value"][idx]
                case "Put credit":
                    self.config.put.credit = new["value"][idx]
                case "Hedge interval":
                    self.config.hedger.hedge_interval = new["value"][idx]
                case "Future interval":
                    self.config.future.interval = new["value"][idx]
                case "Call interval":
                    self.config.call.interval = new["value"][idx]
                case "Put interval":
                    self.config.put.interval = new["value"][idx]
                case _:
                    logger.warn(f"Invalid config field {field}")


class MainUI:
    def __init__(self, exchange: Exchange, config: TradeConfig):
        self.exchange = exchange
        self.config = config

    def ui_root(self, doc: Document):
        manual_control_UI = ManualNewsTradeControlUI(self.config)
        cardsUI = CardsUI(self.config, manual_control_UI)
        theoUI = MonitorTable(self.config)
        futureUI = ControlTable(self.config)
        update_functions = [theoUI.update]

        doc.add_root(
            row(
                column(manual_control_UI.render(), cardsUI.render()),
                column(theoUI.render(), futureUI.render()),
            )
        )

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
