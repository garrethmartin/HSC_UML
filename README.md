# ***README*** for `classify.py` / `graph_clustering`

### Update history

*September 2019*: - HSC DR1 UDEEP catalogue added

*Near future*: - Add DR2 DEEP/UDEEP catalogues with varying *k*
      	       - Add code to run the algorithm w/ examples and documentation

***

### Reference: [***Martin 2019b***](https://address_temp "arXiv...")

### Contact: [garrethmartin@arizona.edu](mailto:garrethmartin@arizona.edu "email")

***

### Purpose:
Clusters objects found in a list of astronomical images by their visual similarity. Objects are sorted into *k* groups and a catalogue containing object centroids, group number, size in pixels and silhouette score is output.

### Prerequisites:
* numpy
* scipy
* astropy
* configobj
* sklearn
* joblib

* [dotnetcore SDK](https://dotnet.microsoft.com/download "dotnetcore")

### Installation:

First install dotnetcore SDK, then run:
    
    sudo python install.py

### Usage:

#### Using the built-in script:

#### Importing the package
