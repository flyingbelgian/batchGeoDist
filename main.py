from tkinter import filedialog
import filehandler
import geocalc

# file1 = filedialog.askopenfilename(title="Select csv file containing 1st set of coordinates.")
# file2 = filedialog.askopenfilename(title="Select csv file containing 2nd set of coordinates.")
file1 = "sample_source.csv"
file2 = "sample_source2.csv"

set1 = filehandler.Source(file1)
set2 = filehandler.Source(file2)

dataset = geocalc.DistSet(set1.coords, set2.coords)

dataset.greatCircle()