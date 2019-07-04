from math import sqrt
import plotly.graph_objs as go
import plotly.io as pio


def apply_restrictions(item, restrictions):
    for i in range(0, len(restrictions), 2):
        if item[restrictions[i]] != restrictions[i + 1]:
            return False
    return True


def get_data_from_file(file, ):
    f = open(file)
    lines = f.readlines()
    header = lines[0].replace('\n', '').split(',')
    data = []
    for line in lines[1:]:
        split = line.replace('\n', '').split(',')
        obj = {}
        for i in range(0, len(split)):
            obj[header[i]] = split[i]
        data.append(obj)
    return data


def get_line_data(data, x_key, y_key, y_error_key, restrictions):
    data.sort(key=lambda k: float(k[x_key]))
    x = list(map(lambda item: float(item[x_key]), filter(lambda item: apply_restrictions(item, restrictions), data)))
    y = list(map(lambda item: float(item[y_key]), filter(lambda item: apply_restrictions(item, restrictions), data)))
    y_error = dict()
    if y_error_key:
        y_error = dict(
            type='data',
            array=list(map(lambda item: sqrt(float(item[y_error_key])),
                           filter(lambda item: apply_restrictions(item, restrictions), data))),
            visible=True
        )
    return x, y, y_error


def create_chart(file, x_key, y_key, options, outfile):

    available_markers = ['circle', 'square', 'diamond', 'cross', 'triangle-up', 'diamond-wide', 'hexagon',
                         'triangle-down',
                         'triangle-left', 'triangle-down', 'pentagon', 'square-cross', 'hexagram']

    data = get_data_from_file(file)
    chart_data = []
    for i in range(0, len(options['lines'])):
        x, y, error_y = get_line_data(data, x_key, y_key, options['variance_key'],
                                      options['restrictions'] + options['lines'][i][1:])
        chart_data.append(go.Scatter(
            x=x,
            y=y,
            name=options['lines'][i][0],
            mode='lines+markers',
            marker=dict(
                symbol=available_markers[i],
                size=10
            ),
            line=dict(width=4),
            error_y=error_y
        ))
    yrange = None
    if options['yrange']:
        yrange = [options['yrange'][0], options['yrange'][1]]
    xrange = None
    if options['xrange']:
        yrange = [options['xrange'][0], options['xrange'][1]]
    layout = dict(title=options['title'],
                  xaxis=dict(
                      title=x_key,
                      dtick=options['xtick'],
                      exponentformat='none',
                      tickformat=options['xformat'],
                      range=xrange
                  ),
                  yaxis=dict(
                    title=y_key,
                    dtick=options['ytick'],
                    exponentformat='none',
                    tickformat=options['yformat'],
                    range=yrange
                  ))

    pio.write_image(dict(data=chart_data, layout=layout), outfile)
