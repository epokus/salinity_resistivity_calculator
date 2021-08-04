from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Row, Column, ranges, LinearAxis, TextInput, Select, Panel, Tabs, Button, Div
import os
import pytz
from datetime import datetime




import numpy as np

def RW (temp, ws):
    return (400000 / temp / ws)**0.88

def SAL(temp, rw):
    return  400000 / temp / (rw**1.14)

def FtoC(degF):
    return (degF - 32) * 5/9

def calc_rw_sal(temp, sal, temp_type):
    if temp_type == 'degC':
        temp = FtoC(temp)

    data_plot = {'temp': [temp],
                 'sal': [sal],
                 'rw': [RW(temp, sal)],
                 'text': [f'Rw: {round(RW(temp, sal), 2)}. temp: {round(temp, 2)} degF. Salinity: {round(sal, 2)}. '], }

    data_plot_line = {'temps': np.arange(50, 400, 5),
                      'rws'  : RW(np.arange(50, 400, 5), sal)}

    return data_plot, data_plot_line


def calc_sal_rw(temp, rw, temp_type):
    if temp_type == 'degC':
        temp = FtoC(temp)

    data_plot = {'temp': [temp],
                 'sal':  [SAL(temp, rw)],
                 'rw':   [rw],
                 'text': [f'Rw: {round(rw, 2)}. temp: {round(temp, 2)} degF. Salinity: {round(SAL(temp, rw), 2)}. '], }

    data_plot_line = {'temps': np.arange(50, 400, 5),
                      'rws'  : RW(np.arange(50, 400, 5), SAL(temp, rw))}

    return data_plot, data_plot_line

def record_data(mode, temp, rw, sal, date):
    if 'record.csv' in os.listdir():
        f = open('record.csv','a+')
    else:
        f = open('record.csv','w+')
    f.write(f'{mode},{temp},{rw},{sal},{date}\n')
    f.close()

salinities = np.array([200, 300, 400, 500, 600, 700, 800, 1000, 1200, 1400, 1700, 2000, 3000, 4000, 5000, 6000, 7000,
                       8000, 10000, 12000, 14000, 17000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 100000,
                       120000, 140000, 170000, 200000, 250000, 280000])

container_x = []
container_y = []
text_x = []
text_y = []
text_s = []
for sal in salinities:
    temp = np.arange(50, 400, 5)
    rw   = RW(temp,sal )
    container_x.append(list(temp))
    container_y.append(list(rw))
    text_x.append(temp[-1])
    text_y.append(rw[-1])
    text_s.append(str(sal)+' ppm')

p = figure(y_axis_type="log", x_range=(50, 425))

p.title = ('Rw - Salinity - Temp Plot')
p.xaxis.axis_label = ('Temp (degF)')
p.yaxis.axis_label = ('Resistivity (ohmmm)')

p.extra_x_ranges = {'Temp (degC)': ranges.Range1d(start=FtoC(50), end=FtoC(425))}
p.add_layout(LinearAxis(x_range_name='Temp (degC)', axis_label = 'Temp (degC)'), 'below', )

p.multi_line(container_x, container_y, line_alpha=0.2, line_color='orange')
p.text(text_x, text_y, text_s,
       angle=-20,angle_units='deg', text_font_size={'value': '8px'})

data_plot, data_plot_line = calc_rw_sal(120, 2500,'degF')
data_plot = ColumnDataSource(data_plot)
data_plot_line = ColumnDataSource(data_plot_line)

p.circle('temp', 'rw', source=data_plot)
p.text('temp', 'rw', 'text',source=data_plot,text_font_size={'value': '8px'})
p.line('temps', 'rws', source=data_plot_line)

err_msg = Div(text='')
headings = Div(text='''<table style="height: 18px; width: 901px; border-collapse: collapse;" border="0">
<tbody>
<tr style="height: 18px;">
<td style="width: 150px; height: 18px;"><img src="https://www.spwla.org/images/Events/indonesia%20logo1.jpg" alt="" width="150" height="84" /></td>
<td style="width: 150px; height: 18px;"><img src="https://universitaspertamina.ac.id/wp-content/uploads/2017/11/logo-Press-103x75.png" alt="" width="110" height="80" /></td>
<td style="width: 591px; height: 18px;">
<h1>Salinity - Calculator Water Resistivity</h1>
.</td>
</tr>
</tbody>
</table>
<p>&nbsp;</p>
''')

footer = Div(text='''
This app is an <a href="https://github.com/epokus/salinity_resistivity_calculator/">open source</a> resource that developed in Collaboration between <a href="https://universitaspertamina.ac.id/">Universitas Pertamina</a> (Epo Prasetya Kusumah) and <a href="http://spwla-indonesia.org/">SPWLA - Indonesian Chapter</a>. Your data (date, data inputs, and button action) will be recorded to improve our app in the future.<br />Any critique or inputs may be directed to <a href="mailto:spwla.indonesia@gmail.com">spwla.indonesia@gmail.com </a>

''')

sal_input = TextInput(value="2500", title="Salinity:")
rw_input  = TextInput(value="0.04", title="Water Resistivity:")
tem_input = TextInput(value="120", title="Temp")
tem_type  = Select(title="Temp Unit:", value="degF", options=["degF", "degC"])

calc_sal_button = Button(label='Calculate')
calc_rw_button = Button(label='Calculate')

rw_temp  = Column(rw_input, tem_input, tem_type, calc_sal_button)
sal_temp = Column(sal_input, tem_input, tem_type, calc_rw_button)

rw_tab  = Panel(child = rw_temp, title='Sal form RW@temp')
sal_tab = Panel(child = sal_temp, title='Rw@temp form Sal')

tabs = Tabs(tabs=[rw_tab, sal_tab])

def calc_sal_button_callback():
    try:
        tz = pytz.timezone('Asia/Jakarta', )
        datetime_tz = datetime.now(tz).strftime("%D %H:%M:%S")
        temp = float(tem_input.value)
        rw   = float(rw_input.value)
        type = tem_type.value

        temp1, temp2 = calc_sal_rw(temp, rw, type)
        data_plot.data      = temp1
        data_plot_line.data = temp2
        err_msg.text = ''''''
        record_data('Rw to get Sal', temp, 0, rw, datetime_tz)

    except:
        err_msg.text = '''<pre>!!! temp, sal, and rw must be a number</pre>'''


    # print('hello', temp, rw, type)

def calc_rw_button_callback():
    try:
        tz = pytz.timezone('Asia/Jakarta', )
        datetime_tz = datetime.now(tz).strftime("%D %H:%M:%S")

        temp  = float(tem_input.value)
        sal   = float(sal_input.value)
        type  = tem_type.value

        temp1, temp2 = calc_rw_sal(temp, sal, type)
        data_plot.data      = temp1
        data_plot_line.data = temp2
        err_msg.text = ''''''
        record_data('Sal to get Rw', temp, sal, 0, datetime_tz)

    except:
        err_msg.text = '''<pre>!!! temp, sal, and rw must be a number</pre>'''

    # print('hello 2', temp, sal, type)

calc_sal_button.on_click(calc_sal_button_callback)
calc_rw_button.on_click(calc_rw_button_callback)

stack = Column(headings, Row(p, Column(tabs, err_msg)),footer)
curdoc().add_root(stack)
curdoc().title='Salinity Calculator - SPWLA'
