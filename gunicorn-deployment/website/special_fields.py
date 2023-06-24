from wtforms import SelectMultipleField, widgets

class MultiCheckField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()
