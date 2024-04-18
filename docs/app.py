import plotly.express as px
from shiny import App, reactive, render, ui
import shinyswatch
from shinywidgets import output_widget, render_plotly, render_widget
import faicons as fa


tips = px.data.tips()

bill_rng = (min(tips.total_bill), max(tips.total_bill))
# 
# Add page title and Side bar
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider("total_bill", "Bill amount", min=bill_rng[0], max=bill_rng[1], value=bill_rng, pre="$",),
        ui.input_checkbox_group("time", "Food Service", ["Lunch", "Dinner"], selected=["Lunch", "Dinner"], inline=False),
        ui.input_checkbox_group("day", "Day", ["Thur", "Fri", "Sat", "Sun"], selected=["Thur", "Fri", "Sat", "Sun"], inline=False),
        ui.input_action_button("reset", "Reset filter", style="background-color: white"),
        
        
        ui.h6("Links:"),
        ui.a(
            "GitHub Source",
            href="https://github.com/Tesfamariam100/cintel-06-custom",
            target="_blank"),
        style="background-color: indigo"  # Set the background color here
    ),
    ui.h4("Restaurant Tipping Insights", style="color: Apricot"),
    ui.layout_columns(
        ui.value_box("Total tippers", ui.output_ui("total_Tippers"), showcase=fa.icon_svg("users"), theme="custom-gradient"),
        ui.value_box("Average Tip Amount", ui.output_ui("average_tip2"), showcase=fa.icon_svg("dollar-sign"), theme="custom-gradient"),
        ui.value_box("Average bill", ui.output_ui("average_bill"), showcase=fa.icon_svg("receipt"), theme="custom-gradient"),
        fill=False),
    
    ui.layout_columns(
        # make data frame
        ui.card(
            ui.card_header("Summary of Tips"),
            ui.output_data_frame("table"),
            full_screen=False,
            theme="bg-gradient-yellow-green"),
        # make scatterplot
        ui.card(
            ui.card_header(
                "Bill Total vs Tips",
                ui.popover(
                    fa.icon_svg("ellipsis"),
                    ui.input_radio_buttons(
                        "scatter_color",
                        None,
                        ["none", "sex", "smoker", "day", "time"],
                        inline=True),
                    title="Add a color variable",
                    placement="top"),
                class_="d-flex justify-content-between align-items-center"),
            output_widget("scatterplot"),
            full_screen=True,
            theme="bg-gradient-blue-green"),
        # make ridgeline plot
        ui.card(
            ui.card_header(
                "Tip Percentages",
                ui.popover(
                    fa.icon_svg("ellipsis"),
                    ui.input_radio_buttons(
                        "tip_perc_y",
                        "Split by:",
                        ["sex", "smoker", "day", "time"],
                        selected="day",
                        inline=False),
                    title="Add a color variable"),
                class_="d-flex justify-content-between align-items-center"),
            output_widget("tip_perc"),
            full_screen=True,
            theme="bg-gradient-purple-indigo"),
        col_widths=[6, 6, 12],
        theme="bg-gradient-gray"),
    fillable=True,
    theme="bg-gradient-light-blue")

def server(input, output, session):
    @reactive.calc
    def tips_data():
        bill = input.total_bill()
        idx1 = tips.total_bill.between(bill[0], bill[1])
        idx2 = tips.time.isin(input.time())
        idx3 = tips.day.isin(input.day())
        return tips[idx1 & idx2 & idx3]

    @render.ui
    def total_tippers():
        return tips_data().shape[0]

    @render.ui
    def average_tip():
        d = tips_data()
        if d.shape[0] > 0:
            perc = d.tip / d.total_bill
            return f"{perc.mean():.1%}"

    @render.ui
    def average_tip2():
        d = tips_data()
        if d.shape[0] > 0:
            perc = d.tip 
            return f"{perc.mean():.2f}" 

    @render.ui
    def average_bill():
        d = tips_data()
        if d.shape[0] > 0:
            bill = d.total_bill.mean()
            return f"${bill:.2f}"

    @render.data_frame
    def table():
        return render.DataGrid(tips_data())

    @render_plotly
    def scatterplot():
        color = input.scatter_color()
        return px.scatter(
            tips_data(),
            x="total_bill",
            y="tip",
            labels={"total_bill":"Bill($)", "tip":"Tip Amount($)"},
            color=None if color == "none" else color,
            trendline="lowess",
            trendline_color_override='indigo')

    @render_plotly
    def tip_perc():
        # Code for tip percentage plot
        pass

    @reactive.effect
    @reactive.event(input.reset)
    def _():
        ui.update_slider("total_bill", value=bill_rng)
        ui.update_checkbox_group("time", selected=["Lunch", "Dinner"])
        ui.update_checkbox_group("day", selected=["Thur", "Fri", "Sat", "Sun"])

app = App(app_ui, server)