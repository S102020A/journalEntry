import toml
import psycopg2


def get_database_credentials(toml_file_path):
    try:
        with open(toml_file_path, "r") as f:
            config = toml.load(f)
            if "postgres" in config:
                return config["postgres"]
            else:
                print("Error: 'postgres' section not found in the TOML file.")
                return None
    except FileNotFoundError:
        raise Exception(f"Error: File not found at {toml_file_path}")
    except toml.TomlDecodeError as e:
        raise Exception("Error decoding TOML file: {e}")


def get_connection():
    credentials = get_database_credentials(".streamlit\secrets.toml")
    return psycopg2.connect(**credentials)
