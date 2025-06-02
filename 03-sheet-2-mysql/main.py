import gspread
from google.oauth2.service_account import Credentials
import mysql.connector
import os
from dotenv import load_dotenv
import datetime

# Load environment variables
load_dotenv()

# Database configuration
DB_NAME = os.getenv("DB_DATABASE")
DB_USER = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
SHEET_NAME = os.getenv("SHEET_NAME")
TRUNCATE_ON_START = os.getenv("TRUNCATE_ON_START").lower()
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")

# Google Sheets configuration
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
gc = gspread.authorize(credentials)

spreadsheet = gc.open(SHEET_NAME)
all_worksheets = spreadsheet.worksheets()

# Connect to MySQL
try:
    connection = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
    )
    cursor = connection.cursor()

    # Iterate through each worksheet
    for worksheet in all_worksheets:
        print(f"\n=== Processing worksheet: {worksheet.title} ===")

        # Get all values from the current worksheet
        data = worksheet.get_all_values()

        if not data:
            print("(No data in this worksheet)")
            continue

        # First row contains column names
        headers = data[0]

        # Check if the first column is an ID column, and skip it if it is
        id_column_index = None
        if headers[0].lower() == "id":
            id_column_index = 0
            print("Skipping ID column to let MySQL auto-increment")

        # Filter out the ID column if present
        filtered_headers = []
        for i, header in enumerate(headers):
            if i != id_column_index:
                filtered_headers.append(header)

        # Rest of the rows are data
        rows = data[1:]

        if not rows:
            print("(No data rows in this worksheet)")
            continue

        # Create table name from worksheet title (replace spaces with underscores and lowercase)
        table_name = worksheet.title.replace(" ", "_").lower()

        # Truncate table if flag is set to True
        if TRUNCATE_ON_START == "true":
            try:
                truncate_query = f"TRUNCATE TABLE `{table_name}`;"
                cursor.execute(truncate_query)
                print(f"Truncated table: {table_name}")
            except mysql.connector.Error as err:
                print(f"Error truncating table: {err}")
                # Continue with insertion even if truncate fails

        # Process in chunks of 100
        chunk_size = 100
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i : i + chunk_size]

            # Generate INSERT statements for this chunk
            print(
                f"Generating MySQL INSERT statements for chunk {i//chunk_size + 1}/{(len(rows) + chunk_size - 1)//chunk_size}"
            )

            # Create insert statement with added created_at and updated_at columns
            column_names = ", ".join([f"`{col}`" for col in filtered_headers])
            column_names += ", `created_at`, `updated_at`"

            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for row in chunk:
                # Escape values properly for MySQL, skipping ID column if present
                values = []
                for j, value in enumerate(row):
                    if j != id_column_index:  # Skip the ID column
                        if value == "":
                            values.append("NULL")
                        else:
                            # Escape single quotes in the data
                            escaped_value = value.replace("'", "\\'")
                            values.append(f"'{escaped_value}'")

                # Add created_at and updated_at values
                values.append(f"'{current_time}'")  # created_at
                values.append(f"'{current_time}'")  # updated_at

                values_str = ", ".join(values)
                insert_query = f"INSERT INTO `{table_name}` ({column_names}) VALUES ({values_str});"

                # Execute the insert query
                try:
                    cursor.execute(insert_query)
                    display_row = [v for i, v in enumerate(row) if i != id_column_index]
                    print(
                        f"Inserted row: {display_row[:3]}..."
                        if len(display_row) > 3
                        else f"Inserted row: {display_row}"
                    )
                except mysql.connector.Error as err:
                    print(f"Error: {err}")

            # Commit after each chunk
            connection.commit()
            print(f"Committed chunk {i//chunk_size + 1}")

        print(f"=== Completed processing worksheet: {worksheet.title} ===\n")

    cursor.close()
    connection.close()
    print("Database connection closed")

except mysql.connector.Error as err:
    print(f"Database Error: {err}")
except Exception as e:
    print(f"Error: {e}")
