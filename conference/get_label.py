import pickle

# open saved chosen file
with open("chosen.pkl", 'rb') as f:
    chosen = pickle.load(f)

def get_label(chosen, basename):
    for key,value in chosen:
        if key == basename:
            return value["label"].split('+')  # list of labels
    return None