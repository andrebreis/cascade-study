import plotly as py
import plotly.graph_objs as go


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
            array=list(map(lambda item: float(item[y_error_key]),
                           filter(lambda item: apply_restrictions(item, restrictions), data))),
            visible=True
        )
    return x, y, y_error


def create_graph(file, x_key, y_key, v_key, title, global_restrictions, lines, outfile):
    data = get_data_from_file(file)
    chart_data = []
    for line in lines:
        x, y, error_y = get_line_data(data, x_key, y_key, v_key, global_restrictions + line[1:])
        chart_data.append(go.Scatter(
            x=x,
            y=y,
            name=line[0],
            error_y=error_y
        ))
    layout = dict(title=title,
                  xaxis=dict(title=x_key),
                  yaxis=dict(title=y_key))
    py.offline.plot(dict(data=chart_data, layout=layout), filename=outfile)
