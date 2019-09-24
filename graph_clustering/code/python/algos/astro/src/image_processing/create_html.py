import os
import re
import random
import numpy as np


def sort_func(x):
    m = re.match('labels_([0-9]+)_([0-9]+)', x)
    if m:
        a = int(m.group(1))
        return a
    else:
        return 9999


d = '/data/ryanjackson/candels2/tests/model0/conncomps/'


folders = filter(lambda x: os.path.isdir(os.path.join(d, x)), os.listdir(d))
folders = sorted(folders, key=lambda x: sort_func(x))

# create outer folder
table = '<html><head></head><body><h1>Min galaxy size: 20</h1>'
for folder in folders:
    #m = re.match('k([0-9]+)_([0-9]+)_([a-z]+)', folder)
    m = re.match('labels_([0-9]+)_([0-9]+)_([0-9]+)_([kmeans|agg])', folder)
    if m == None:
        print("skipping folder: {0}".format(folder))
        continue
    numk = m.group(1)
    minpixels = m.group(2)
    #norm = m.group(3)
    #title = 'number of clusters: {0}  min galaxy size (in pixels): {1}'.format(numk, minpixels)
    title = 'number of clusters: {0}'.format(numk)
    table += '<p>\n'
    table += "<a href='{0}/index.html'>{1}</a>\n".format(folder, title)
    table += '</p>\n'
table += '</body><html>'

file = open(d + 'index.html', 'w')
file.write(table)
file.close()


for folder in folders:
    folder_path = os.path.join(d, folder)
    #m = re.match('k([0-9]+)_([0-9]+)', folder)
    m = re.match('labels_([0-9]+)_([0-9]+)_([0-9]+)_([kmeans|agg])', folder)
    if m == None:
        print ("skipping folder: {0}".format(folder))
        continue
    numk = m.group(1)
    minpixels = m.group(2)
    title = 'Number of clusters: {0}  Minimum number of pixels: {1}'.format(numk, minpixels)
    table = '<html><head><title>{0}</title></head><body><h2>{1}</h2><p>Images ordered by silhouette score (+1 good, -1 bad)</p>\r\n'.format(folder, title)
    image_folders = filter(lambda x: os.path.isdir(os.path.join(folder_path, x)), os.listdir(folder_path))
    for image_folder in image_folders:
        print (folder + image_folder)
        #images = np.array(filter(lambda x: x.endswith('.png'), os.listdir(os.path.join(folder_path, image_folder))))
        images = list(filter(lambda x: x.endswith('.png'), os.listdir(os.path.join(folder_path, image_folder))))
        images = np.array(images)
        #if len(images) > 50:
        #    rand_50_indices = np.random.choice(len(images), 50, replace=False)
        #    images = images[rand_50_indices]

        gals = []
        for image_idx in range(len(images)):
            image = images[image_idx]
            # galaxy_6_585_plus0dot012872
            #m_image = re.match('galaxy_([0-9]+)_([0-9]+)_(plus|minus)([0-9])+dot([0-9]+).png', image)
            m_image = re.match('galaxy_([0-9]+)_([0-9]+)_([0-9]+)_(plus|minus)([0-9])+dot([0-9]+)_([a-z]+).png', image)
            #output_cutout_name = output_folder + '/galaxy_{0}_{1}_{2}_{3}_{4}.png'.format(sky_area_id, type, obj_id,
            #                                                                              sil_val,
            #                                                                              field_code[sky_area_id])
            if m_image is None:
                print (image)
                continue
            id = m_image.group(3)
            sign = m_image.group(4)
            if sign == "plus":
                sign = ""
            else:
                sign = "-"
            main = m_image.group(5)
            decs = m_image.group(6)
            s_score = sign + main + '.' + decs
            s_score = float(s_score)
            gals.append((s_score, id, image))

        gals = sorted(gals, key=lambda x: x[0], reverse=True)

        table += '<div style="clear:both;"><h2>Cluster {0}:</h2>'.format(image_folder)
        counter = 0
        for gal in gals:
            gal_score = gal[0]
            gal_id = gal[1]
            gal_url = gal[2]
            table += "<div id='thumbnail' style='float:left; font-size: 10px;'>\r\n<table><tr><td>\r\n"
            table += '<img src="{0}" alt="{1}" style="margin:1px;float:left;"></img>\r\n</td></tr><tr><td align="middle">\r\n<span style="font-size: 14px;">'.format(image_folder + '/' + gal_url, gal_id)
            table += '{0}</span>\r\n</td></tr></table>\r\n</div>\r\n'.format(gal_score)
            counter += 1
            if counter > 50:
                break
        table += '</div>'



    table += '</body></html>'
    print(folder_path + '/index.html')
    file = open(folder_path + '/index.html', 'w')
    file.write(table)
    file.close()


"""
        table += '<div style="clear:both;"><h1>Cluster_{0}</h1>'.format(image_folder)
        for image_idx in range(len(images)):
            image = images[image_idx]
            # galaxy_6_585_plus0dot012872
            m_image = re.match('galaxy_([0-9]+)_([0-9]+)_(plus|minus)([0-9])+dot([0-9]+).png', image)
            if m_image is None:
                print image
                continue
            id = m_image.group(2)
            sign = m_image.group(3)
            if sign == "plus":
                sign = ""
            else:
                sign = "-"
            main = m_image.group(4)
            decs = m_image.group(5)
            table += "<div id='thumbnail' style='float:left; font-size: 10px;'><table><tr><td>"
            table += '<img src="{0}" alt="{1}" style="margin:1px;float:left;"></img></td></tr><tr><td align="middle"><span style="font-size: 14px;">'.format(image_folder + '/' + image, id)
            table += '{0}{1}.{2}</span></td></tr></table></div>'.format(sign, main, decs)
            #if image_idx % 10 == 0 and image_idx > 0:
            #    table += '</section><section>'
        table += '</div>'
"""
