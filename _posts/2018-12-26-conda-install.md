---
title: 'Installing Miniconda'
date: 2018-12-26
permalink: /posts/2018/12/conda-install/
-- tags:
  - conda
  - installation
  - setup
---

Installing Miniconda on Linux, Mac OS X, and Windows 10 for point-cloud processing, python programming, and work with GMT, CDO and other tools.

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
It is useful to install different environments for different purposes. Here is a list of useful environments with different purposes:
For some of these examples, you want to add:
```bash
conda config --prepend channels conda-forge/label/dev
conda config --prepend channels conda-forge
```

| What for? | Conda commands |
|:----------|:--------------|
| Pandoc Processing | ```conda create -y -n pandoc python pip pandoc imagemagick``` |
| GMT 5 and Python Processing |```conda create -y -n gmt5 gmt=5* python=3.6 scipy pandas numpy matplotlib scikit-image gdal spyder imagemagick``` |
| GMT 6 and Python Processing |```conda create -y -n gmt6 gmt=6* python=3* scipy pandas numpy matplotlib scikit-image gdal spyder imagemagick``` |
| GMT and CDO Processing | ```conda create -y -n gmt5_cdo gmt=5* cdo imagemagick```<br>There appears to be an issue with some cdo version (libhdf) and you may need to install cdo separately.  |
| CDO Processing | ```conda create -y -n cdo cdo```<br>For some miniconda installations, you have to separately install CDO into a different environment, because of hdf library versioning issues. |
| CDO and NCL Processing | ```conda create -y -n cdo_ncl cdo ncl imagemagick```  |
|PointCloud Processing | ```conda create -y -n PC_py3 python=3.6 pip scipy pandas numpy matplotlib scikit-image gdal pdal xarray packaging ipython multiprocess h5py lastools pykdtree spyder gmt=5* imagemagick``` <br> Activate the environment ```source activate PC_py3``` <br> and install laspy with ```pip install laspy```|


# Activating environments
You can now call ```source activate pandoc``` to start the pandoc environment. Alternatively, you can set an alias in your .bashrc file.
