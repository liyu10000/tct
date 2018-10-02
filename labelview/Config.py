from easydict import EasyDict as edict

__C = edict()
cfg = __C

# classes used checkboxes
__C.CLASSES = ["ASCUS", "LSIL", "ASCH", "HSIL", "SCC", "AGC1", "AGC2",
           	   "ADC", "EC", "FUNGI", "TRI", "CC", "ACTINO", "VIRUS",
           	   "MC", "SC", "RC", "GEC"]

# color used in display of checkboxes and patches on thumbnail image
__C.COLOURS = {'AGC3': '#ff55ff', 'ASCUS': '#00557f', 'FUNGI': '#00aa00', 
           	   'LSIL': '#005500', 'SCC': '#0055ff', 'EC': '#aa55ff', 
           	   'ASCH': '#aa007f', 'VIRUS': '#55aa7f', 'SC': '#aa00ff', 
           	   'RC': '#ff0000', 'AGC2': '#ff557f', 'MC': '#000000', 
           	   'CC': '#00aaff', 'ACTINO': '#55aa00', 'HSIL': '#aa0000', 
           	   'ADC': '#aa557f', 'TRI': '#00aa7f', 'AGC1': '#ff5500', 
           	   'GEC': '#aa5500'}

# color used in xml
__C.CONVERT = {'#000000': 'MC', '#aa55ff': 'EC', '#005500': 'LSIL', 
               '#00557f': 'ASCUS', '#ff557f': 'AGC2', '#00aaff': 'CC', 
               '#aa5500': 'GEC', '#00aa7f': 'TRI', '#ff0000': 'RC', 
               '#00aa00': 'FUNGI', '#0055ff': 'SCC', '#55aa7f': 'VIRUS', 
               '#ff55ff': 'AGC3', '#aa557f': 'ADC', '#55aa00': 'ACTINO', 
               '#ff5500': 'AGC1', '#aa007f': 'ASCH', '#aa00ff': 'SC', 
               '#aa0000': 'HSIL'}