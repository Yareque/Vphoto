# Vphoto

Computes statistics on section of images.

The link to the images is in csv file.  An example is vess.csv.  The csv file has three columns
     image_id, image_source, region
     image_id is a text indetifier of the iamge
     image_source is either a path to a file, can be relative of abosulte, or a URL pointing to a jpg file
     region is a quoted text of a 4 element tuple in the form of "(0.1, 0.2, 0.9, 0.8)"
             ths specfies a relative region within the image in fraction of the height or width
             the specifications are (left, top, right, bottom)
             
The statisitcs provide are in a Pandas data frame.  The column identifers are 
     image_id, image_source, region
     image_id is a text indetifier of the iamge
     med_r  = median of the red channel of part of the image defined by region
     med_g  = median of the green channel
     med_b  = median of the blue channel
     cv_r = coefficent of variance for red 
     cv_g = coefficent of variance for green
     cv_b = coefficent of variance for blue  
     med_h = median of the hue channel in the HSV coor space (0 to 360 range)
     med_s = median of the saturation channel  (0 to 1 ramge)
     med_v = median of the value channel  (0 to 1 ramge)
     
usage is found in the example file vphoto_test.py

