import panel as pn
import numpy as np
import matplotlib.pyplot as plt
from bokeh.plotting import figure

# Create a sine wave plot using Matplotlib
x = np.linspace(0, 10, 200)
y = np.sin(x)
plt.plot(x, y)
plt.title('Sine Wave')
mpl_pane = pn.pane.Matplotlib(plt.figure(), tight=True)

# Create a random scatter plot using Bokeh
x = np.random.random(size=200) * 100
y = np.random.random(size=200) * 100
p = figure(title='Random Scatter Plot', x_axis_label='X', y_axis_label='Y')
p.circle(x, y, size=10, color='navy', alpha=0.5)
bokeh_pane = pn.pane.Bokeh(p)

# Create a Panel dashboard with the two plots
dashboard = pn.Row(mpl_pane, bokeh_pane)
coming
# Save the dashboard as an HTML file
dashboard.save('dashboard.html', embed=True)