# Welcome! 

Within this respository are a few convenience functions to assist with the pulling and pushing of data from the Notion API.
Given your credential file and database you want to access, you can pull back a cleanly formatted json tables to lookup by table row_id or by database field name.
For each type of object in the Notion database I am extracting only core information - the value or the plain text by the data-parsing functions.
You can access the raw data from the api for your custom parsing by using `.raw_data` of the NotionData class object.
Please note, not every type of field is accounted for in this custom parsing. 

**Field types which are implemented include:**
- date (takes single input and returns start and end dates formatted in python datetime format for convenience)
- relation
- text
- rich_text
- title
- select
- checkbox

I do not plan on implementing additional field types at this time - if you need additional functionality please feel free to fork this repo and/or submit a pull request.
These scripts are provided without guarantee or warrenty; as of writing this, all scripts have worked for my purposes - and I will continue to update the code as I notice changes within my own projects.
Please note that Notion has tweaked how different field types return data a few times recently which may cause breakage.

# Quickstart:
```
notion_data = NotionData(DATABASE_ID, INTEGRATION_TOKEN)
notion_data.summary #quick summary of returned records and structure of first record
notion_data.data #returns the full raw data for custom json parsing
notion_data.fields #returns all fields in database for reference
notion_data.field_types #returns the field types of the fields for custom logic on parsing the json based on elements specific to a type
notion_data.row_ids #unique match-keys that represent a row within a data table
```
# Looking up a specific column values:
`notion_data.query_field()['field_name']`

# Looking up a specific id values: 
`notion_data.query_id()['row_id']`

# Searching using regex to return all records matching the lookup:
```
# Returns matching ids & record data
match_pattern = r'testlookup' #appropriate re.match regex string
my_lookup = notion_data.lookup(match_pattern, field)
my_lookup[0] #matching id values
my_lookup[1] #records cooresponding to id values

```
