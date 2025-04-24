import subprocess
import sys
import os
import argparse
import pandas as pd
from fnmatch import fnmatch

def combine_csvs_by_columns(directory, output_csv="metadata/combined_raw_data.csv", pattern="GSE*_raw.csv"):
    """
    Finds all CSV files matching a pattern in a directory and its subdirectories,
    and concatenates them into one DataFrame based on column names,
    ordering the columns in a specific way.

    Args:
        directory (str): The directory to start the search from.
        output_csv (str, optional): The name of the output CSV file. Defaults to "combined_data.csv".
        pattern (str, optional): The file name pattern to match. Defaults to "*.csv".
    """

    all_data = pd.DataFrame()  # Initialize an empty DataFrame

    for root, _, files in os.walk(directory):
        for file in files:
            if fnmatch(file, pattern):  # Use fnmatch for pattern matching
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_csv(file_path)
                    all_data = pd.concat([all_data, df], ignore_index=True, sort=True)  # Concatenate DataFrames
                    print(f"Appended: {file_path}")
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    # Define the desired column order
    first_columns = ['sample_geo_accession', 'sample_library_strategy', 'sample_contact_name',
                     'sample_submission_date', 'sample_name', 'big_key', 'genotype',
                     'sample_source_name_name_ch1']
    remaining_columns = [col for col in all_data.columns if col not in first_columns]
    column_order = first_columns + remaining_columns

    # Reindex the DataFrame with the desired column order
    all_data = all_data.reindex(columns=column_order)

    all_data.to_csv(output_csv, index=False)  # Save the combined DataFrame to a CSV file
    print(f"Finished combining CSV files into {output_csv} with specified column order.")



def check_conda_env_exists(env_name):
    """Checks if the Conda environment exists."""
    try:
        result = subprocess.run(['conda', 'env', 'list'], capture_output=True, text=True, check=True)
        return env_name in result.stdout
    except subprocess.CalledProcessError:
        return False


def main():
    """
    Main function to check for Conda, the environment, create it if
    necessary, and then execute the main script logic.  This script is intended to be run by the user,
    *not* from within a Conda environment.
    """
    env_name = "meta_geofetch"
    env_file = "environment.yml"

    # Check for Conda installation
    try:
        subprocess.run(['conda', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Conda is not installed. Please install Miniconda or Anaconda and ensure it's in your system's PATH.")
        sys.exit(1)

    # Check for Conda environment and create if it doesn't exist
    if not check_conda_env_exists(env_name):
        print(f"Conda environment '{env_name}' does not exist. Creating it...")
        try:
            subprocess.run(['conda', 'env', 'create', '-n', env_name, '-f', env_file], check=True, capture_output=True, text=True)
            print(f"Conda environment '{env_name}' created successfully from {env_file}.")
        except subprocess.CalledProcessError as e:
            print(f"Error creating Conda environment: {e}")
            sys.exit(1)
        except FileNotFoundError:
            print("Error: conda command not found.")
            sys.exit(1)
    else:
        print(f"Conda environment '{env_name}' already exists.")



    parser = argparse.ArgumentParser(description="Fetch GEO metadata, process GSEs, and combine raw CSV files.")
    parser.add_argument("search_string", help="The GEO search query (e.g., 'h3k4me3 AND mouse AND oocyte')")
    parser.add_argument("-o", "--output_file", dest="output_list_file", default="metadata/metadata.txt",
                        help="The path to save the list of found GSE accessions (default: metadata/metadata.txt)")
    parser.add_argument("--discard_soft", action="store_true", help="Discard soft files during geofetch")
    parser.add_argument("--raw_data_dir", dest="raw_data_directory", default=".",
                        help="The directory to search for raw CSV files for combining (default: current working directory)")
    parser.add_argument("--combined_output_csv", dest="combined_output_csv", default="combined_raw_data.csv",
                        help="The name of the output CSV file after combining raw data (default: combined_raw_data.csv)")
    parser.add_argument("--raw_data_pattern", dest="raw_data_pattern", default="*_raw.csv",
                        help="The file name pattern to match for raw CSV files (default: *_raw.csv)")

    args = parser.parse_args()

    # Call the main script logic here
    search_string = args.search_string
    output_list_file = args.output_list_file
    discard_soft = args.discard_soft
    raw_data_directory = args.raw_data_directory
    combined_output_csv = args.combined_output_csv
    raw_data_pattern = args.raw_data_pattern

    # Call the functions
    user_script_main(search_string, output_list_file, discard_soft, raw_data_directory, combined_output_csv, raw_data_pattern)



def user_script_main(search_string, output_list_file, discard_soft, raw_data_directory, combined_output_csv, raw_data_pattern):
    # --- Python Part 1: Fetch GSEs and save to a list file ---
    try:
        from geofetch import Finder
        os.makedirs(os.path.dirname(output_list_file), exist_ok=True)
        gse_obj = Finder(filters=search_string)
        gse_list = gse_obj.get_gse_all()
        print(f"Found the following GSEs: {gse_list}")

        with open(output_list_file, 'w') as f:
            for gse in gse_list:
                f.write(f"{gse}\n")
        print(f"GSE list written to {output_list_file}")

    except ImportError:
        print("Error: The 'geofetch' library is not installed. Please install it using 'pip install geofetch'.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred during GSE finding: {e}")
        sys.exit(1)

    # --- Bash Part (executed using Python): Process each GSE ---
    if not os.path.isfile(output_list_file):
        print(f"Error: Input file '{output_list_file}' not found.")
        sys.exit(1)

    try:
        with open(output_list_file, 'r') as f:
            for line in f:
                gse = line.strip()
                if gse:
                    output_filename = f"metadata/metadata_{gse}.txt"
                    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
                    command = ["geofetch", "--just-metadata", "--discard-soft", "-i", gse, "-u", "metadata/"]
                    process = subprocess.run(command, check=True, capture_output=True, text=True)
                    print(f"Processed GSE: {gse}, metadata saved to {output_filename}")
                    if process.stderr:
                        print(f"Error output for GSE {gse}: {process.stderr}")

    except FileNotFoundError:
        print(f"Error: Input file '{output_list_file}' not found.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error executing geofetch for GSE {gse}: {e}")
        print(f"Stderr: {e.stderr}")
        pass
    except Exception as e:
        print(f"An error occurred during metadata fetching: {e}")
        pass

    print("Finished processing all GSEs.")

    # --- Python Part 2: Combine raw CSV files ---
    print("\n--- Combining raw CSV files ---")
    combine_csvs_by_columns(raw_data_directory, output_csv=combined_output_csv, pattern=raw_data_pattern)



if __name__ == "__main__":
    main()

