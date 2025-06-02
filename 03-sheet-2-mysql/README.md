# Google Sheet to MySQL data migration

This code will allow you to migrate data from Google sheets to MySQL.

You need to create a Google Developer app and download the credentials JSON file for this script to work.

# Features
1. Adds created_at and updated_at to every row and added automatically
2. Configuration provided to truncate tables before import through .env
3. Supports n number of tabs (name should match the table name)
4. Supports n number of columns in sheet (name should match with column name)
5. ID columns of each table are incremented automatically and the ID column of sheet will be ignored
6. Data is inserted in chunks of 100
