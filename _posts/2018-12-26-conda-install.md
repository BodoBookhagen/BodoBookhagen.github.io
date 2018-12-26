---
title: 'Notes for Computer Networks'
date: 2018-12-26
permalink: /posts/2018/12/conda-install/
<!-- tags:
  - cool posts
  - category1
  - category2 -->
---

# Installing Conda on Linux, Mac OS X, and Windows 10

## Installation on Windows 10
Installation works best, if you use the Windows 10 Bash. There are several resources available on the internet that explain the [bash setup](https://www.windowscentral.com/how-install-bash-shell-command-line-windows-10). 
After the reboot, *wget* [miniconda](https://conda.io/miniconda.html) for [Linux 64 bit](https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh) and install:

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

## Installation on Linux
This is a Python 3.x code that will run on any OS, which supports the packages. It runs and has been tested on Linux (Ubuntu/Debian), Windows 10, and Mac OS X. We are using [conda/miniconda](https://conda.io/docs/) to install the required packages, which can be [downloaded here](https://conda.io/miniconda.html). Follow [these instruction](https://conda.io/docs/user-guide/install/index.html) to get miniconda installed. In short:
```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

# Installing environments
There exists different environments for different purposes. Here is a list of useful environments that have different purposes:
For some of these examples, you want to add:
```bash
conda config --prepend channels conda-forge/label/dev
conda config --prepend channels conda-forge
```

| What for? | Conda commands|
|:----|:----:|
PointCloud Processing | ```
conda create -y -n PC_py3 python=3.6 pip scipy pandas numpy matplotlib \
	scikit-image gdal pdal xarray packaging ipython multiprocess \
	h5py lastools pykdtree spyder gmt=5* imagemagick
``` 
Activate the environment and install laspy
```bash
source activate PC_py3
pip install laspy
```
|

