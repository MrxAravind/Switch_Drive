import pickle
import datetime
import os


def read_all_entries():
    file_path = 'db.bin'
    try:
        entries = []
        with open(file_path, 'rb') as binary_file:
            while True:
                try:
                    entry = pickle.load(binary_file)
                    entries.append(entry)
                except EOFError:
                    break  # End of file reached

        return entries
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except pickle.UnpicklingError as e:
        print(f"Error reading from binary file: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None

def write_to_binary(entry_data):
    file_path = 'db.bin'
    if not os.path.exists(file_path):
        data = {'next_id': 1, 'entries': []}
    else:
        while True:
            try:
                # Load existing data
                with open(file_path, 'rb') as existing_file:
                    data = pickle.load(existing_file)
                break  # Break the loop if successful
            except Exception as e:
                print(f"Error loading existing data: {str(e)}")
                # Retry or handle the error as needed

    entry_data['id'] = data['next_id']
    entry_data['uploaded_time'] = datetime.datetime.now().strftime("%H:%M:%S")
    data['next_id'] += 1
    data['entries'].append(entry_data)

    try:
        with open(file_path, 'wb') as binary_file:
            pickle.dump(data, binary_file)
        print(f"Data successfully written to binary file: {file_path}")
    except Exception as e:
        print(f"Error writing to binary file: {str(e)}")




def read_from_binary():
    file_path = 'db.bin'
    try:
        # Create the file if it doesn't exist
        if not os.path.exists(file_path):
            with open(file_path, 'wb') as create_file:
                pickle.dump({'next_id': 1, 'entries': []}, create_file)

        with open(file_path, 'rb') as binary_file:
            data = pickle.load(binary_file)
        print(f"Data successfully read from binary file: {file_path}")
        return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except pickle.UnpicklingError as e:
        print(f"Error reading from binary file: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None









"""
# Data to be written to binary file
sample_data = {
    'username': 'john_doe',
    'file_id': 'example_file_id',
    'filename': 'example_file.txt',
    'file_size': 1024,  # in bytes
}

# Write data to binary file
write_to_binary(sample_data)

# Read data from binary file
read_data = read_from_binary()

# Print the read data
if read_data:
    print("Read Data:", read_data)


"""