# meta-geofetch
## Introduction
meta-geofetch is a bioinformatics semi-automatic pipeline to fetch metadata from Gene Expression Omnibus (GEO) database.
This tool is particularly useful when planning a complex analysis with various samples. Especially if:
- Samples are retreived using a variety of keywords
- Data needs to be inspected/filtered for sample selection

Additionally, this improves geofetch Python package for Mac users (see below).

## Usage

```python meta_geofetch.py [GEO query]```

This generates a list of GSEs from given GEO search query and writes it to metadata.txt
metadata.txt is then processed, retrieving metadata of files associated with given GSEs. 

## Requirements
1. geofetch (Python package)  
    a. coloredlogs  
    b. logmuse  
    c. peppy  
