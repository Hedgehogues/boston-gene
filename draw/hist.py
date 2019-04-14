import io
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


def build_hist(res, bins):
    # TODO: move params image generation to config
    fig = Figure(figsize=(15, 10))
    axis = fig.add_subplot(1, 1, 1)
    axis.hist(res, bins=bins)
    fontsize = 18
    axis.set_title("Distribution of gene's expression", fontsize=fontsize)
    axis.set_xlabel("Values of gene's expression", fontsize=fontsize)
    axis.set_ylabel("Count values", fontsize=fontsize)
    # axis.set_xticks(fontsize=fontsize)
    # axis.set_yticks(fontsize=fontsize)
    axis.grid(True)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')
