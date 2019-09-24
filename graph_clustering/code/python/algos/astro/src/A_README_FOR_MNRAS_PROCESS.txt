This is the process used to create the data and figures for the gng and hc mnras paper.

In algos/astro/code
and algos/astro/exp1/cutouts (only for histograms_pymorph_with_mag_galfit.py)
1. Run threshold_hst_images.py to get the sigma levels using sigma clipping
    you can choose most of the image (exluding 0s on the edge). but only one figure so find a nice blank bit.
    use 3 sigma
2. Run the feature_extraction.py process
3. Run GNG  .net
4. Run HC   .net
1b. Run object_detection_mask_creation.py to get list of patches above the two sigmas

5. Run connected components to get catalogue
6. Run NN   .net
7. galaxy analysis to output graphs of the pca of the galaxy sample vectors
8. galaxy train to get the centroids of the two groups of galaxies
9. produce catalogue object_sigma_levels.py to add sigmas to the objects ???1

application to new image
1. Run object simgma levels
2. run the feature_extraction.py using the std and mean of the learnt image
3. run NN
4. run connected components to get catalogue
5. run nn on the galaxy sample vectors to get classifications

5.5 run algos/astro/exp1/cutouts/montage_149.py to get cutouts for pymorph
6. run pymorph on 435 and 814 separately
    this will output the sextractor values and m20, gini, cas etc for each galaxy

7. run histograms_pymorph_with_mag_galfit.py on the output of pymorph
    this will output plots for colour mag and m20, gini etc

8. run astro_montage_pngs.py for creating nice image plots for the paper (also STIFF for making RGBs)

