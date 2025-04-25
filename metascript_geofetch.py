import subprocess
from geofetch import Finder
import argparse
import os
import pandas as pd
from fnmatch import fnmatch

def combine_csvs_by_columns(directory, output_csv=None, pattern="gse*_raw.csv"):
    """
    Finds all CSV files matching a pattern in a directory and its subdirectories,
    and concatenates them into one DataFrame based on column names,
    ordering the columns in a specific way. It also formats the 'sample_contact_name' column.

    Args:
        directory (str): The directory to start the search from.
        output_csv (str, optional): The name of the output CSV file. If None, returns the DataFrame.
        pattern (str, optional): The file name pattern to match. Defaults to "*.csv".
    """
    all_data = pd.DataFrame()  # initialize an empty dataframe
    files_found = False #added

    for root, _, files in os.walk(directory):  # Change to os.walk to recurse subdirectories
        for file in files:
            if fnmatch(file, pattern):  # use fnmatch for pattern matching
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_csv(file_path)
                    # Format 'sample_contact_name' if it exists (case-insensitive check)
                    for col in df.columns:
                        if col.lower() == 'sample_contact_name':
                            print(f"Found column: {col}")
                            print(f"Data before formatting:\n{df['sample_contact_name'].head()}")
                            df['sample_contact_name'] = df['sample_contact_name'].apply(format_contact_name)
                            print(f"Data after formatting:\n{df['sample_contact_name'].head()}")
                            print(f"Formatted column: {col}")
                            break
                    else:
                        print(f"'sample_contact_name' column not found in {file_path}")

                    all_data = pd.concat([all_data, df], ignore_index=True, sort=False)  # concatenate dataframes
                    print(f"appended: {file_path}")
                    files_found = True #set to true
                except Exception as e:
                    print(f"error reading {file_path}: {e}")

    # define the desired order for the initial columns
    first_columns_set = ['sample_geo_accession', 'development_stage', 'genotype', 'treatment',
                            'sample_library_strategy', 'antibody', 'sample_contact_name',
                            'sample_submission_date', 'sample_name', 'big_key']

    # Get the actual first columns present in the data
    first_columns = [col for col in first_columns_set if col in all_data.columns]

    # Define the columns to appear at the position after the two empty separators
    middle_columns_set = ['sample_source_name_ch1', 'organism']

    # Get the actual middle columns present in the data
    middle_columns = [col for col in middle_columns_set if col in all_data.columns]

    # Get the remaining columns, excluding those in first_columns_set and middle_columns_set
    remaining_columns = [col for col in all_data.columns if col not in first_columns_set and col not in middle_columns_set]

    column_order = first_columns + ['separator_1', 'separator_2'] + remaining_columns + middle_columns

    # reindex the dataframe with the desired column order
    all_data = all_data.reindex(columns=column_order)

    if output_csv:
        all_data.to_csv(output_csv, index=False)  # save the combined dataframe to a csv file
        print(f"finished combining csv files into {output_csv} with specified column order and separator columns.")
        return all_data
    elif files_found: #check if files were found
        return all_data
    else:
        return None
def format_contact_name(name):
    """
    Formats a contact name string from "First,,Last" to "LastF".

    Args:
        name (str): The contact name string.

    Returns:
        str: The formatted contact name, or the original name if formatting fails.
    """
    if not isinstance(name, str) or not name:  # Handle non-string or empty input
        return name
    parts = name.split(',,')
    if len(parts) >= 2:
        first_name = parts[0].strip()
        last_name = parts[-1].strip()
        if first_name and last_name:
            return f"{last_name}{first_name[0]}"
    return name  # Return the original name if the format is not as expected

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="fetch geo metadata, process gses, combine and filter raw csv files.")
    parser.add_argument("search_string", nargs='?', help="the geo search query (e.g., 'h3k4me3 and mouse and oocyte')")
    parser.add_argument("--organism", nargs='?', help="filter combined data by organism name")
    parser.add_argument("--assay", nargs='?', help="filter combined data by assay type (sample_library_strategy)")
    parser.add_argument("--target", nargs='?', help="filter combined data by target string in sample name (case-insensitive)")
    parser.add_argument("-o", "--output_file", dest="output_list_file", default="metadata/metadata.txt",
                            help="the path to save the list of found gse accessions (default: metadata/metadata.txt)")
    parser.add_argument("--discard_soft", action="store_true", help="discard soft files during geofetch")
    parser.add_argument("--raw_data_dir", dest="raw_data_directory", default=".",
                            help="the directory to search for raw csv files for combining (default: current working directory)")
    parser.add_argument("--combined_output_csv", dest="combined_output_csv", default="combined_raw_data.csv",
                            help="the name of the output csv file after combining raw data (default: combined_raw_data.csv)")
    parser.add_argument("--raw_data_pattern", dest="raw_data_pattern", default="*_raw.csv",
                            help="the file name pattern to match for raw csv files (default: *_raw.csv)")

    args = parser.parse_args()

    search_string = args.search_string
    organism_filter = args.organism
    assay_filter = args.assay
    target_filter = args.target
    output_list_file = args.output_list_file
    discard_soft = args.discard_soft
    raw_data_directory = args.raw_data_directory
    combined_output_csv = args.combined_output_csv
    raw_data_pattern = args.raw_data_pattern

    if search_string is None:
        search_string = input("Enter GEO search query: ")
    if organism_filter is None:
        organism_filter = input("Enter organism name (for filtering, optional): ").strip()
    else:
        organism_filter = organism_filter.strip()

    if assay_filter is None:
        assay_filter = input("Enter assay type (for filtering 'sample_library_strategy', optional): ").strip()
    else:
        assay_filter = assay_filter.strip()

    if target_filter is None:
        target_filter = input("Enter target string in sample name (for filtering, case-insensitive, optional): ").strip()
    else:
        target_filter = target_filter.strip()

    # --- python part 1: fetch gses and save to a list file ---
    try:
        os.makedirs(os.path.dirname(output_list_file), exist_ok=True)
        gse_obj = Finder(filters=search_string)
        gse_list = gse_obj.get_gse_all()
        print(f"found the following gses: {gse_list}")

        with open(output_list_file, 'w') as f:
            for gse in gse_list:
                f.write(f"{gse}\n")
        print(f"gse list written to {output_list_file}")

    except ImportError:
        print("error: the 'geofetch' library is not installed. please install it using 'pip install geofetch'.")
        exit(1)
    except Exception as e:
        print(f"an error occurred during gse finding: {e}")
        exit(1)

    # --- bash part (executed using python): process each gse ---
    if not os.path.isfile(output_list_file):
        print(f"error: input file '{output_list_file}' not found.")
        exit(1)

    metadata_dir = "metadata"
    try:
        with open(output_list_file, 'r') as f:
            for line in f:
                gse = line.strip()
                if gse:
                    gse_dir = os.path.join(metadata_dir, gse) #create path for each gse
                    if not os.path.exists(gse_dir): #check if the directory exists
                        output_filename = f"{metadata_dir}/metadata_{gse}.txt"
                        os.makedirs(os.path.dirname(output_filename), exist_ok=True)
                        command = ["geofetch", "--just-metadata", "--discard-soft", "-i", gse, "-u", f"{metadata_dir}/"]
                        process = subprocess.run(command, check=True, capture_output=True, text=True)
                        print(f"processed gse: {gse}, metadata saved to {output_filename}")
                        if process.stderr:
                            print(f"error output for gse {gse}: {process.stderr}")
                    else:
                        print(f"GSE directory {gse_dir} already exists, skipping download") # Added skipping
    except FileNotFoundError:
        print(f"error: input file '{output_list_file}' not found.")
        exit(1)
    except subprocess.CalledProcessError as e:
        print(f"error executing geofetch for gse {gse}: {e}")
        print(f"stderr: {e.stderr}")
        pass
    except Exception as e:
        print(f"an error occurred during metadata fetching: {e}")
        pass

    print("finished processing all gses.")

    # --- python part 2: combine raw csv
    print("\n--- combining raw csv files ---")
    # changed raw_data_directory to metadata
    combined_df = combine_csvs_by_columns(metadata_dir, output_csv=combined_output_csv, pattern=raw_data_pattern)
    print(combined_df)
    if combined_df is not None and not combined_df.empty:
        print("\n--- applying filters ---")
        filtered_df = combined_df.copy()  # Create a copy to avoid modifying the original

        # Apply filters independently
        if organism_filter:
            print(f"filtering by organism: '{organism_filter}' in 'organism' column (case-insensitive)")
            filtered_df = filtered_df[filtered_df['organism'].str.contains(organism_filter, na=False, case=False)]

        if assay_filter:
            print(f"filtering by assay type: '{assay_filter}' in 'sample_library_strategy' column (case-insensitive)")
            filtered_df = filtered_df[filtered_df['sample_library_strategy'].str.contains(assay_filter, na=False, case=False)]

        if target_filter:
            print(f"filtering by target: '{target_filter}' in 'sample_name' column (case-insensitive)")
            filtered_df = filtered_df[filtered_df['sample_name'].str.lower().str.contains(target_filter.lower(), na=False, case=False)]

        output_csv_filtered = combined_output_csv.replace(".csv", "_filtered.csv")
        filtered_df.to_csv(output_csv_filtered, index=False)
        print(f"filtered data saved to {output_csv_filtered}")

        # Rename metadata directory and move filtered CSV
        if target_filter:
            new_metadata_dir = target_filter
            print(f"Target directory: {new_metadata_dir}") #added
            print(f"Metadata directory: {metadata_dir}") #added
            if os.path.exists(metadata_dir):
                try:
                    os.rename(metadata_dir, new_metadata_dir)
                    print(f"renamed directory '{metadata_dir}' to '{new_metadata_dir}'")
                    # Move the filtered CSV file
                    try:
                        print(f"Moving {output_csv_filtered} to {new_metadata_dir}") #added
                        print(f"Moving {combined_output_csv} to {new_metadata_dir}") #added
                        os.rename(output_csv_filtered, os.path.join(new_metadata_dir, output_csv_filtered))
                        os.rename(combined_output_csv, os.path.join(new_metadata_dir, combined_output_csv)) # Move the combined CSV
                        print(f"moved {output_csv_filtered} and {combined_output_csv} to {new_metadata_dir}")
                    except Exception as e:
                        print(f"error moving filtered and combined csv: {e}")
                except Exception as e:
                    print(f"error renaming directory: {e}")
                    pass
            else:
                print(f"error: directory '{metadata_dir}' not found.")
        else:
            print("target filter was empty, will not rename metadata directory")
    else:
        print("no data to combine and filter.")


