from pathlib import Path, PurePath
import logging
import numpy as np


class MassSpectrum(object):
    def __init__(self, master):
        self.logger = logging.getLogger(__name__)
        self.axes = master.axes
        self.filename = master.filename
        self.open_mass_spectrum()

    def baseline_correct(self):
        x_values, y_values = zip(*self.data)
        y_average = np.average(y_values)
        y_std = np.std(y_values)

        subset = [(x, y) for (x, y) in self.data if y >= y_average-y_std and
                  y <= y_average+y_std]
        x_subset, y_subset = zip(*subset)

        p = np.polynomial.polynomial.polyfit(x_subset, y_subset, 3)
        f = np.poly1d(p)

        self.data = [(x, y-f(x)) for x, y in self.data]

    def open_mass_spectrum(self):
        file_type = None
        with Path(self.filename).open() as fr:
            for line in fr:
                # Prototype (File Recognition)
                if 'utter_nonsense' in line:
                    file_type = 'Bruker'

        if file_type == None:
            try:
                self.open_xy_spectrum()
            except Exception as e:
                self.logger.error(e)

    # Potentially move this to a dedicated IO module ?
    def open_xy_spectrum(self):
        data_buffer = []
        with Path(self.filename).open() as fr:
            for line in fr:
                line = line.rstrip().split()
                data_buffer.append((float(line[0]), float(line[-1])))
        self.data = data_buffer

    def plot_mass_spectrum(self):
        label = PurePath(self.filename).stem
        x_array, y_array = zip(*self.data)
        self.axes.plot(x_array, y_array, label=str(label))

def finalize_plot(master):
    master.axes.set_xlabel('m/z [Th]')
    master.axes.set_ylabel('Intensity [au]')
    handles, labels = master.axes.get_legend_handles_labels()
    master.axes.legend(handles, labels)
    master.axes.get_xaxis().get_major_formatter().set_useOffset(False)
    master.canvas.draw_idle()