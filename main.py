from tkinter import filedialog
import filehandler
import geocalc

# file1 = filedialog.askopenfilename(title="Select csv file containing 1st set of coordinates.")
# file2 = filedialog.askopenfilename(title="Select csv file containing 2nd set of coordinates.")
file1 = "sample_refpts.csv"
file2 = "sample_source.csv"

refpts = filehandler.Source(file1)
assesspts = filehandler.Source(file2)

dataset = geocalc.DistSet(refpts.coords, assesspts.coords)

filehandler.write_csv(file2, dataset.dataframe)