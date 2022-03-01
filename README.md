# Terra Synchroniser
A tool for synchronizing a [Terra](https://app.terra.bio) data table with a local directory.

The tool enables the user to specify:
- namespace 
- workspace
- entity-type (sample, participant, etc.)
- specific rows (by name or regexp applied to name)
- columns (by name of regexp applied to name)

The selected attributes can be placed in a json file and the files 
(i.e. values that look like "gs://<bucket>/<something>) will be downloaded to a specified directory with the following
directory structure:
```
-- <user specified>/
  |-- <row name>/
      |-- <column name>/
         |-- <filename>
```


# To use
The tool's operation is specified by a yaml file which specified "actions" that are to be taken in 
sequence each one modifying a list of data:

###query
Gets all the entities from a specified datatable:
```yaml
- action: query 
    name: (optional) name for commenting
    namespace: name-space-of-workspace
    workspace: name-of-workspace
    entity: entity-type-of-data-table
```

### subset
subsets the data according to the values of the name of the entity
```yaml
- action: subset 
    name: (optional) name for commenting
    values:
      - a list of values 
      - that will be looked for
      - in the entity ids
    regexps:
      - a list of regular expressions
      - that will be applied to the 
      - entity ids   
```
An entity will be included if its name is in the list of values, or 
satisfies any of the regular expressions

### select
Chooses a set of columns according to their names, with a set of specified values, and regualr expressions
```yaml
- action: select 
    name: (optional) 
    values:
      - a list of values 
      - that will be looked for
      - in the column names
    regexps:
      - a list of regular expressions
      - that will be applied to the 
      - column names   
```
An column will be included if its name is in the list of values, or 
satisfies any of the regular expressions

### sample
Will "sample" the first rows from the data according to a parameter:
```yaml
- action: sample
  name: take 10 rows from the top
  head: 10
```
### localize
Download attributes that "look like" gcs objects (i.e. start with "gs://")
also adds simple checksum (crc32) and the local path to the downloaded path to the data. 
Prior to downloading, if the local file exists, the crc of the local file will be compared 
to that of the remote file and if they are the same, localization will not occur. 
```yaml
- action: localize
  name: localize things that look like gs:// files. 
  comment: |
    "map" enables an attribute to be localized to a subdirectory not specified by it's name. 
    This can come in handy when wanting to localize an index to the same subdir as a main 
    file (bam, vcf, reference, etc.)
  map:
    attribute_index:attr_main
  directory: path-to-top-of-local-data
```

### write
writes the data to a local json file.
```yaml
- action: write
  name: write data to a local file
  output: file-name-for-data.json
```






