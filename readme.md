# meta-geofetch
## Introduction
meta-geofetch is a bioinformatics semi-automatic pipeline to fetch metadata from Gene Expression Omnibus (GEO) database.
This tool is particularly useful when planning a complex analysis with various samples. Especially if:
- Samples are retreived using a variety of keywords
- Data needs to be inspected/filtered for sample selection

Additionally, this improves geofetch Python package for Mac users (see below).

## Usage

```python meta_geofetch.py```  
```Enter GEO search query: [your_GEO_query]```  
```Enter organism name (for filtering, optional): [latin organism name]```  
```Enter assay type (for filtering, optional): [i.e. ChIP-seq]```  
```Enter target string in sample_name (for filtering and renaming the metadata directory)```


This generates a list of GSEs from given GEO search query and writes it to metadata.txt  
metadata.txt is then processed, retrieving metadata of files associated with given GSEs.
Metadata then might be filtered using provided filters and concatenated into one file.


## Requirements
``` conda create -f environment.yml```  
``` conda activate meta_geofetch```

## Citations
https://doi.org/10.1093/bioinformatics/btad069
```bibtex
@article{10.1093/bioinformatics/btad069,
    author = {Khoroshevskyi, Oleksandr and LeRoy, Nathan and Reuter, Vincent P and Sheffield, Nathan C},
    title = "{GEOfetch: a command-line tool for downloading data and standardized metadata from GEO and SRA}",
    journal = {Bioinformatics},
    volume = {39},
    number = {3},
    pages = {btad069},
    year = {2023},
    month = {03},
    abstract = "{The Gene Expression Omnibus has become an important source of biological data for secondary analysis. However, there is no simple, programmatic way to download data and metadata from Gene Expression Omnibus (GEO) in a standardized annotation format.To address this, we present GEOfetch—a command-line tool that downloads and organizes data and metadata from GEO and SRA. GEOfetch formats the downloaded metadata as a Portable Encapsulated Project, providing universal format for the reanalysis of public data.GEOfetch is available on Bioconda and the Python Package Index (PyPI).}",
    issn = {1367-4811},
    doi = {10.1093/bioinformatics/btad069},
    url = {https://doi.org/10.1093/bioinformatics/btad069},
    eprint = {https://academic.oup.com/bioinformatics/article-pdf/39/3/btad069/49407404/btad069.pdf},
}
```
