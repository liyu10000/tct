import pickle

# open saved chosen file
with open("chosen.pkl", 'rb') as f:
    chosen = pickle.load(f)

def get_label(chosen, basename):
    for class_i,entries in chosen.items():
        for entry in entries:
            if entry[0] == basename:
                return entry[1]["label"].split('+')  # list of labels
    return None