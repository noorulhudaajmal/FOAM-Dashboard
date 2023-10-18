from enum import Enum


class Widgets(Enum):
    TITLE = 1
    SUB_TITLE = 2
    HEAD_TITLE = 3
    COLORS = 5


def get_widgets_formats(widget_type: Widgets):
    match widget_type:
        case Widgets.TITLE:
            return """
                <div style="background-color:{};padding:10px;border-radius:10px">
                <h1 style="color:{};text-align:center;">{}</h1>
                </div>
                """
        case Widgets.SUB_TITLE:
            return """
                <div style="background-color:{};padding:0.5px;border-radius:5px;">
                <h4 style="color:{};text-align:center;">{}</h6>
                </div>
                """
        case Widgets.HEAD_TITLE:
            return """<h6 style="text-align:left;margin-top:2px">{}</h6>"""

        case Widgets.COLORS:
            return ["#2a9d8f", "#74a57f", "#8ab17d", "#8bb174", "#e9c46a", "#efb366", "#f4a261", "#ee8959",
                    "#e76f51", "#e76f51", "#e76f51", "#e76f51", "#e76f51", "#e76f51", "#e76f51", "#e76f51",
                    "#e76f51", "#e76f51", "#e76f51", "#e76f51", "#e76f51", "#e76f51", "#e76f51", "#e76f51",
                    "#e76f51", "#e76f51", "#e76f51", "#e76f51"]

def format_currency_label(value):
    if value >= 1e9:  # Billion
        return f'{value / 1e9:.2f} bn'
    elif value >= 1e6:  # Million
        return f'{value / 1e6:.2f} M'
    elif value >= 1e3:  # Thousand
        return f'{value / 1e3:.2f} K'
    else:
        return f'{value:.2f}'