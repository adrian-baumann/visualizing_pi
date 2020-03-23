# first of all the imports

import math
import numpy as np
import pandas as pd

import requests
from bs4 import BeautifulSoup

import matplotlib.pyplot as plt
import matplotlib.collections as mcoll
import matplotlib.path as mpath


def get_pi_as_string():
    """
    Take the digits of Pi from a website as a string, remove spaces, decimal points and linebreaks and return it.
    If you want a higher or lower number of Pi's digits, you can change the number of zeroes in the websites url.
    They have up to one million digits.
    """

    request = requests.get("http://www.eveandersson.com/pi/digits/10000")
    doc = BeautifulSoup(request.text, "html.parser").select_one("pre").text.strip()
    pi_string = doc.replace(" ", "").replace(".", "").replace("\n", "")
    return pi_string


def generate_xy_coords(amount_of_digits=None):
    """
    Generate a pandas dataframe, calculate the coordinates of the digits of Pi and return it.
    """

    pi_string = get_pi_as_string()

    # if I do not specify exactly how many digits I want to see, I use all available
    if amount_of_digits is None:
        amount_of_digits = len(pi_string)

    pi_dataframe = pd.DataFrame(np.zeros(shape=(amount_of_digits, 3)), columns=["number", "x", "y"])

    current_x_value = 0
    current_y_value = 0

    # because I want to represent pi's digits as vectors on a circle,
    # I distribute the numbers 0 to 9 on the circle by using 2 x pi divided by 10,
    # because I use 10 numbers and calculate x and y with sin and cos
    for counter_index, number in enumerate(pi_string[0:amount_of_digits]):
        number = int(number)
        current_x_value += math.sin(number * (2 * np.pi) / 10)
        current_y_value += math.cos(number * (2 * np.pi) / 10)
        pi_dataframe.iloc[counter_index] = [number, current_x_value, current_y_value]

    origin = pd.DataFrame(
        {'number': 0, 'x': 0, 'y': 0}, index=[0]
    )

    # using pandas' concat I add the origin on top and reset the index
    pi_dataframe = pd.concat([origin, pi_dataframe]).reset_index(drop=True)

    return pi_dataframe


def make_segments(x, y):
    """
    Create list of line segments from the x and y coordinates I provide, in the correct format
    for LineCollection: an array of the form numlines x (points per line) x 2 (x
    and y) array
    """

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    return segments


def colorline(
        x, y, z=None,
        cmap=plt.get_cmap('copper'), norm=plt.Normalize(0.0, 1.0),
        linewidth=0.5, alpha=1.0
):
    """
    http://nbviewer.ipython.org/github/dpsanders/matplotlib-examples/blob/master/colorline.ipynb
    http://matplotlib.org/examples/pylab_examples/multicolored_line.html
    Plot a colored line with coordinates x and y
    Optionally specify colors in the array z
    Optionally specify a colormap, a norm function and a line width
    """

    # Default colors equally spaced on [0,1]:
    if z is None:
        z = np.linspace(0.0, 1.0, len(x))

    # Special case if a single number:
    if not hasattr(z, "__iter__"):  # to check for numerical input -- this is a hack
        z = np.array([z])

    z = np.asarray(z)

    segments = make_segments(x, y)
    line_collection = mcoll.LineCollection(segments, array=z, cmap=cmap, norm=norm,
                                           linewidth=linewidth, alpha=alpha)

    ax = plt.gca()
    ax.add_collection(line_collection)

    return line_collection


fig, ax = plt.subplots()
fig.set_facecolor('whitesmoke')
pi_coords = generate_xy_coords()

path = mpath.Path(np.column_stack([np.array(pi_coords.x), np.array(pi_coords.y)]))
verts = path.interpolated(steps=3).vertices
x, y = verts[:, 0], verts[:, 1]
z = np.linspace(0, 1, len(x))
colorline(x, y, z, cmap=plt.get_cmap('jet'), linewidth=0.3)
plt.ylim((
    min(pi_coords.y) - max(abs(pi_coords.y)) * 0.1,
    max(pi_coords.y) + max(abs(pi_coords.y)) * 0.1
))
plt.xlim((
    min(pi_coords.x) - max(abs(pi_coords.x)) * 0.1,
    max(pi_coords.x) + max(abs(pi_coords.x)) * 0.1
))
ax.axis('off')
plt.tight_layout()
plt.show()
