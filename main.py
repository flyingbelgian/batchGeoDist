from tkinter import filedialog
import tkinter as tk
import filehandler
import geocalc

file1 = filedialog.askopenfilename(title="Select csv file containing reference points.")
file2 = filedialog.askopenfilename(title="Select csv file containing points to be assessed.")
# file1 = "sample_gridpts.csv"
# file2 = "sample_gridpts.csv"

refpts = filehandler.Source(file1)
assesspts = filehandler.Source(file2)

window = tk.Tk()
window.config(padx=20)
window.title("Select Reference Points")
instruction = tk.Label(window,
                       text=f"Select the points from\n{file1}\nto be used as reference points:",
                       justify="left")
instruction.pack(pady=20, anchor="w")

checked = []
for i in range(len(refpts.coords)):
    refpt = refpts.coords[i]['id']
    variable = tk.BooleanVar()
    t = tk.Checkbutton(window, variable=variable, text=refpt)
    checked.append(variable)
    t.pack(anchor="w")

selected = []


def getValues():
    count = 0
    for variable in checked:
        if variable.get():
            selected.append(refpts.coords[count]['id'])
        count += 1
    window.quit()


run = tk.Button(window, text="Save", command=getValues)
run.pack(pady=20)

window.mainloop()

refpts.filterData('id', selected)

dataset = geocalc.DistSet(refpts.coords, assesspts.coords)

filehandler.write_csv(file2, dataset.dataframe)
