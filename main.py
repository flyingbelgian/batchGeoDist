from tkinter import filedialog
import filehandler
import geocalc

# file1 = filedialog.askopenfilename(title="Select csv file containing 1st set of coordinates.")
# file2 = filedialog.askopenfilename(title="Select csv file containing 2nd set of coordinates.")
file1 = "sample_source.csv"
file2 = "sample_source2.csv"

refpts = filehandler.Source(file1)
assesspts = filehandler.Source(file2)

dataset = geocalc.DistSet(refpts.coords, assesspts.coords)

print(dataset.geodist)