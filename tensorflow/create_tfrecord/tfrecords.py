""" this script aims to write image data into TFRecords file
follows this link: https://kwotsin.github.io/tech/2017/01/29/tfrecords.html
the file tree should be like this:
flowers\
    flower_photos\
        tulips\
            ....jpg
            ....jpg
            ....jpg
        sunflowers\
            ....jpg
        roses\
            ....jpg
        dandelion\
            ....jpg
        daisy\
            ....jpg
Note: Your dataset directory will be path/to/flowers and not path/to/flowers/flower_photos. Make sure you do not have any other folders beyond flower_photos in the flowers root directory!
"""

