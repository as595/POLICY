import json
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection

def radar_factory(num_vars, frame='circle'):
    """Create a radar chart with `num_vars` axes.

    This function creates a RadarAxes projection and registers it.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    frame : {'circle' | 'polygon'}
        Shape of frame surrounding axes.

    """
    # calculate evenly-spaced axis angles
    theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)
    # rotate theta such that the first axis is at the top
    theta += np.pi/2

    def draw_poly_patch(self):
        verts = unit_poly_verts(theta)
        return plt.Polygon(verts, closed=True, edgecolor='k')

    def draw_circle_patch(self):
        # unit circle centered on (0.5, 0.5)
        return plt.Circle((0.5, 0.5), 0.5)

    patch_dict = {'polygon': draw_poly_patch, 'circle': draw_circle_patch}
    if frame not in patch_dict:
        raise ValueError('unknown value for `frame`: %s' % frame)

    class RadarAxes(PolarAxes):

        name = 'radar'
        # use 1 line segment to connect specified points
        RESOLUTION = 1
        # define draw_frame method
        draw_patch = patch_dict[frame]

        def fill(self, *args, **kwargs):
            """Override fill so that line is closed by default"""
            closed = kwargs.pop('closed', True)
            return super(RadarAxes, self).fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super(RadarAxes, self).plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.concatenate((x, [x[0]]))
                y = np.concatenate((y, [y[0]]))
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            return self.draw_patch()

        def _gen_axes_spines(self):
            if frame == 'circle':
                return PolarAxes._gen_axes_spines(self)
            # The following is a hack to get the spines (i.e. the axes frame)
            # to draw correctly for a polygon frame.

            # spine_type must be 'left', 'right', 'top', 'bottom', or `circle`.
            spine_type = 'circle'
            verts = unit_poly_verts(theta)
            # close off polygon by repeating first vertex
            verts.append(verts[0])
            path = Path(verts)

            spine = Spine(self, spine_type, path)
            spine.set_transform(self.transAxes)
            return {'polar': spine}

    register_projection(RadarAxes)
    return theta


def unit_poly_verts(theta):
    """Return vertices of polygon for subplot axes.

    This polygon is circumscribed by a unit circle centered at (0.5, 0.5)
    """
    x0, y0, r = [0.5] * 3
    verts = [(r*np.cos(t) + x0, r*np.sin(t) + y0) for t in theta]
    return verts


def example_data(input_data):
	
	keys = list(input_data.keys())
	counts = list(input_data.values())

	data = [
	    keys,
	    ('Policy@Manchester', [ 
	    	counts ])
	]

	return data


def example_data_by_year(input_data):
    
	keys = list(input_data[0].keys())

	all_counts=[]
	for i in range(0,len(input_data)):
		counts = list(input_data[i].values())
		all_counts.append(counts)

	
	data = [
	    keys,
	    ('Policy@Manchester', 
	    	all_counts )
	]

	return data


def get_cats(blogs):

	categories = {
		'Europe': 0,
		'All posts': 0,
		'Brexit': 0,
		'British Politics': 0,
		'Science and Engineering': 0,
		'Westminster Watch': 0,
		'Devo': 0,
		'Health and Social Care': 0,
		'Featured': 0,
		'Science and Technology': 0,
		'Budget 2017': 0,
		'Urban': 0,
		'Energy and Environment': 0,
		'Inclusive Growth': 0,
		'Growth and Inclusion': 0,
		'Whitehall Watch': 0,
		'Polling Observatory': 0,
		'Ethnicity': 0
	}

	for blog in blogs:

		cats = blog["categories"]
		for cat in cats:
			if cat in categories:
				categories[cat] += 1
			else:
				categories[cat] = 1

	categories["Science and Technology"] += categories["Science and Engineering"]

	del categories["Science and Engineering"]
	del categories["All posts"]
	del categories["Featured"]
	del categories["Budget 2017"]

	return categories


def get_cats_by_year(in_year,blogs):

	categories = {
		'Europe': 0,
		'All posts': 0,
		'Brexit': 0,
		'British Politics': 0,
		'Science and Engineering': 0,
		'Westminster Watch': 0,
		'Devo': 0,
		'Health and Social Care': 0,
		'Featured': 0,
		'Science and Technology': 0,
		'Budget 2017': 0,
		'Urban': 0,
		'Energy and Environment': 0,
		'Inclusive Growth': 0,
		'Growth and Inclusion': 0,
		'Whitehall Watch': 0,
		'Polling Observatory': 0,
		'Ethnicity': 0
	}

	for blog in blogs:

		# find the date of the article:
		date = blog["time"]
		# extract dmy
		month,day,year = date.split()
		#remove the comma after the day
		day=day[:-1]

		if (year==str(in_year)):
			cats = blog["categories"]
			for cat in cats:
				if cat in categories:
					categories[cat] += 1
				else:
					categories[cat] = 1
		else:
			continue

	categories["Science and Technology"] += categories["Science and Engineering"]

	del categories["Science and Engineering"]
	del categories["All posts"]
	del categories["Featured"]
	del categories["Budget 2017"]

	return categories



# ==========================================================================================	
# ==========================================================================================	

if __name__ == '__main__':

	filename = "manchester_blogs.json"

	input_file  = file(filename, "r")
	blogs = json.loads(input_file.read().decode("utf-8-sig"))

	years = [2013,2014,2015,2016,2017]

	#categories = get_cats(blogs)
	all_years = []
	for year in years:
		categories = get_cats_by_year(year,blogs)
		all_years.append(categories)

	N = len(categories)
	theta = radar_factory(N, frame='polygon')

	#data = example_data(categories)
	data = example_data_by_year(all_years)
	
	spoke_labels = data.pop(0)
	
	fig, axes = plt.subplots(figsize=(8,8), nrows=1, ncols=1,
	                         subplot_kw=dict(projection='radar'))

	fig.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)

	colors = ['b', 'r', 'g', 'm', 'y']

	# Plot the four cases from the example data on separate axes
	for ax, (title, case_data) in zip([axes], data):
		ax.set_rgrids([20,40,60,80])
		ax.set_title(title, weight='bold', size='medium', position=(0.5, 1.1),
		             horizontalalignment='center', verticalalignment='center')

		for d, color in zip(case_data, colors):
		    ax.plot(theta, d, color=color)
		    ax.fill(theta, d, facecolor=color, alpha=0.25)

		ax.set_varlabels(spoke_labels)


	# add legend relative to top-left plot
	#ax = axes[0, 0]
	labels = ('2013', '2014', '2015', '2016', '2017')
	legend = ax.legend(labels, loc=(0.9, .95),
	                   labelspacing=0.1, fontsize='small')

	fig.text(0.5, 0.965, '5-Year Policy@Manchester Blog Trends',
	         horizontalalignment='center', color='black', weight='bold',
	         size='large')

	plt.savefig("category_by_year.png")
	plt.show()
	plt.close(fig)

	
