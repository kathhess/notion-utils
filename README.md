# Welcome! 

Within this respository are a few convenience functions to assist with the pulling and pushing of data from the Notion API.
Given your credential file and database you want to access, you can pull back cleanly formatted json tables to lookup by database row_id or field name.
For each type of object in the Notion database, I am using pre-defined functions to extract only core information - the field value or the plain text.
You can access the raw data by using `.raw_data` of the NotionData class object.
Please note, not every type of field is accounted for in this custom parsing. 

**Field types which are implemented include:**
- date (takes single input and returns start and end dates formatted in python datetime format for convenience)
- relation (returns relation IDs which can be passed back through .query_id() to return record information)
- text (returns plain text value)
- rich_text (returns plain text value)
- title (returns plain text value)
- select (returns plain text value)
- checkbox (returns True False boolean based on if box was checked)

I do not plan on implementing additional field types at this time - if you need additional functionality please feel free to fork this repo and/or submit a pull request. These scripts are provided without guarantee or warrenty; as of writing this, all scripts have worked for my purposes and I will continue to update the code as I notice data structure changes within my own projects. Please note that any changes to how Notion returns field type data may lead to breakage.

# Quickstart:
```
notion_data = NotionData(DATABASE_ID, INTEGRATION_TOKEN)
notion_data.summary() #quick summary of returned records and structure of first record
notion_data.data #returns the full raw data for custom json parsing
notion_data.fields #returns all fields in database for reference
notion_data.field_types #returns the field types of the fields for custom logic on parsing the json based on elements specific to a type
notion_data.row_ids #unique match-keys that represent a row within a data table
```
# Return all row_id & values for a given field:
`notion_data.query_field()['field_name']`

# Return all record information for a given row_id: 
`notion_data.query_id()['row_id']`

# Searching using regex to return all records matching the lookup:
```
# Returns matching ids & record data
match_pattern = r'testlookup' #appropriate re.match regex string
my_lookup = notion_data.lookup(match_pattern, field)
my_lookup[0] #matching id values
my_lookup[1] #records corresponding to id values

```
