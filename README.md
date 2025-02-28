# MetadataExplorer

MetadataExplorer is a tool that aggregates paths and values from multiple JSON files across directories, providing a comprehensive view of all unique JSON paths and their values in a single output. This enables easy analysis and comparison of JSON data across different schemas and repositories. The tool produces two Excel files with aggregated JSON path data at varying levels of granularity.

## Features
- Aggregates JSON paths from multiple files within multiple directories.
- Supports JSON files of varying schemas, including metadata schemas.
- Consolidates identical JSON paths, aggregating values across all directories and files.
- Outputs two Excel files with different levels of aggregation.

---

## Input Directory Structure
MetadataExplorer requires a specific directory structure for processing:
- The root directory must contain subdirectories named in the format (repository_type_name)repository_name.
    - repository_type_name: The type of repository (e.g., CKAN, Dataverse).
    - repository_name: The name of the repository from which the JSON files were sourced.
- Each subdirectory should contain only JSON files.
- Update the directory path in main.py:
  
  directory_path = 'C:/PythonProjects/Lunaris/metadataExplorer/data'

## Output Files
1. **Leaves Directory**:
   - Contains files where each file stores values for a unique JSON path aggregated across all files and directories.

2. **Excel Reports**:
   - repository_paths_merged.xlsm: Aggregates JSON path data at the repository level.
   - repository_types_paths_merged.xlsm: Aggregates JSON path data at the repository type level.
   
   Each Excel file includes the following columns:

     | Column                            | Description |
     |-----------------------------------| ----------- |
     | repo_type/repo                    | Name of the repository type or repository. |
     | path                              | Unique JSON path aggregated across directories. |
     | values_file_path                  | Hyperlink to another Excel file with the aggregated values for the JSON path. |
     | repo_type_total_values/repo_total_values | Count of all values (including duplicates) across directories for this path. |
     | repo_type_missing_values/repo_missing_values | Count of null or empty values for this JSON path across directories. |
     | repo_type_total_items/repo_total_items | Total JSON files processed across directories. |
     | repo_type_items                   | Number of JSON files containing this JSON path. |
     | used_by_repo_types and Used by Lunaris | Reserved for future internal use by Lunaris. |

## Viewing Aggregated Values
Clicking the hyperlink in the `values_file_path` column opens another Excel file displaying all values for the corresponding JSON path across files and directories. This Excel file contains:
1. Repository Type: The type of repository the value was extracted from.
2. Repository Name: The repository name the value was extracted from.
3. File Name: The name of the JSON file containing the value.
4. Original JSON Link: Hyperlink to the JSON file with the corresponding path and value.
5. Value: The extracted value.

This setup allows for an organized, in-depth view of JSON data, making it easy to analyze patterns across multiple data sources and schemas.

Note: json file names are assumed to be unique across all files and directories.


## Dependencies  
Install required packages:  
```bash
pip install pandas openpyxl pywin32
```

## VBA Access Issue  
MetadataExplorer generates Excel reports using VBA. Windows may block programmatic access, causing the error:  
**"Programmatic access to Visual Basic Project is not trusted."**  
To resolve, follow [this guide](https://stackoverflow.com/questions/25638344/programmatic-access-to-visual-basic-project-is-not-trusted).
