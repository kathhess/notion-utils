import requests
import pandas as pd
import numpy as np
from datetime import datetime as dt
import re

class NotionData:
    """
    Given a database id and integration token, store data from notion.
    Get raw data with .data
    """

    def __init__(self, database_id, integration_token):
        self.database_id = database_id
        self.token = integration_token

        database_url = 'https://api.notion.com/v1/databases/' + self.database_id + '/query'
        response = requests.post(database_url, headers={'Authorization': f'{self.token}'})
        if response.status_code != 200:
            raise Exception(f'Response Status: {response.status_code}')
        else:
            self.data = response.json()
        
    @property
    def fields(self):
        """
        Extract fields from raw data.
        Note that not every row has data for every field; 
        need to make sure that we're returning all possible field values
        across all rows.
        """
        all_fields = []
        for i in range(len(self.data['results'])):
            one_rows_fields = list(self.data['results'][i]['properties'].keys())
            all_fields += one_rows_fields
        return set(all_fields)

    @property
    def field_types(self):
        """
        Extract field type to dictionary for each field in database.
        """
        field_type_dict = {}
        for i in range(len(self.data['results'])):    #for each record in database
            try: #if the record has the field, check the type
                for field in self.fields: 
                        field_type = self.data['results'][i]['properties'][field]['type']
                        #update the dictionary with that field & type
                        field_type_dict[field] = field_type
            except KeyError: #pass if the record doesn't have the field (Key Error)
                pass
        return field_type_dict

    @property
    def row_ids(self):
        """
        Returns the unique row id for each item in a database.
        """
        return [self.data['results'][i]['id'] \
        for i in range(len(self.data['results']))]

    def summary(self):
        """
        Return summary information about the structure of the returned data.
        """
        print('Records returned: ' + str(len(self.data['results'])))
        print('Structure: ')
        return self.data['results'][0]

    def query_field(self):
        """
        This function is to extract data to a simple dictionary that can be queried based on the field.
        For each field in data:
        - 1) identify datatype;
        - 2) return dictionaries for each field
        Output: {field: {id: value}}
        """
        field_dict = self.field_types #returns for every row in db: {field: type}
        all_data = {}

        for key in field_dict:
            field_type = field_dict[key]
            field = key
            data_formatted = DataFormatted(self.data, field)

            # depending on each type, process and return data
            # output: {field: {id: value}}

            if field_type == 'text':
                all_data[field] = data_formatted.text()
            if field_type == 'rich_text':
                all_data[field] = data_formatted.rich_text()
            if field_type == 'title':
                all_data[field] = data_formatted.title()
            if field_type == 'relation':
                all_data[field] = data_formatted.relation()
            if field_type == 'date':
                all_data[field+'_start'] = data_formatted.date()[0]
                all_data[field+'_end'] = data_formatted.date()[1]
            if field_type == 'select':
                all_data[field] = data_formatted.select()
            if field_type == 'checkbox':
                all_data[field] = data_formatted.checkbox()

        return all_data
    
    def query_id(self):
        """
        For each row_id in data:
            - 1) identify datatype;
            - 2) return dictionaries for each row_id
        output: {row_id: {field: value}}
        """
        # for row in dataset add to dictionary: 
        # structure: {row_id: {field: value, field: value, ...}, row_id: ...}

        all_data = {}
        field_dict = self.field_types # returns: {field: type}
        data_len = len(self.data['results'])

        for i in range(data_len):
            current_row = self.data['results'][i]
            record_id = current_row['id']

            # create row dictionary such that: {field: value, field: value, ...}
            row_dict = {}

            for key in field_dict: #key == field; subsetting data to each row & passing row value
                # for each column in each row identify row type
                # extract value and update row_dict with new {field: value, ...}
                field = key
                field_type = field_dict[key]
                row_num = i
                data_formatted = DataFormatted(self.data, field, row_num)

                if field_type == 'text':
                    row_dict[field] = list(data_formatted.text().values())[0]
                if field_type == 'rich_text':
                    row_dict[field] = list(data_formatted.rich_text().values())[0]
                if field_type == 'title':
                    row_dict[field] = list(data_formatted.title().values())[0]
                if field_type == 'relation':
                    row_dict[field] = list(data_formatted.relation().values())[0]
                if field_type == 'date':
                    row_dict[field+'_start'] = list(data_formatted.date()[0].values())[0]
                    row_dict[field+'_end'] = list(data_formatted.date()[1].values())[0]
                if field_type == 'select':
                    row_dict[field] = list(data_formatted.select().values())[0]

            #append row dictionary {field: value, ...} to id {row_id: {field: value}}
            all_data[record_id] = row_dict

        return all_data

    def lookup(self, match_pattern, field):
        """
        Based on whether a field or an id is provided, parse tables for data.
        Regex match pattern to filter data.
        Returns list of matching ids, and all information for that record.
        """
        
        notion_dict = self.query_field()[field]
        id_list = []
        item_list = notion_dict.items()

        for item in item_list:
            dict_key = item[0]
            dict_value = item[1]
            #matches pattern, add it to list of key values
            if dict_value == None:
                pass
            else:
                if re.match(match_pattern, dict_value):
                    id_list.append(dict_key)
        
        #return all records associated with lookup ids:
        returned_records = []

        for each_id in id_list:
            returned_records.append(self.query_id()[each_id])

        return id_list, returned_records

class DataFormatted:
        """
        Parse different data types based on their values.
        Pass row_num to define specific row to examine.
        """

        def __init__(self, data, field, row_num=None):
            self.data = data
            self.field = field
            self.row_num = row_num
            self.data_len = len(data['results'])

        def table():
            #field_types
            pass
        
        def current_row(self, i=None):
            """
            Helper function - returns current row of data split into record_id and row data.
            """
            #return row data based on either row_num filter or iteration over dataset
            if self.row_num is not None:
                row_data = self.data['results'][self.row_num]
            if self.row_num is None:
                row_data = self.data['results'][i]

            record_id = row_data['id'] #return the record_id for given row

            return record_id, row_data

        def date(self):
            """
            Extracts the start and end time from a date field.
            Translates from iso format to python datetime.
            Reverse: field.isoformat()

            Scenarios:
            - No start (may not exist)
            - No end:
                - has time
                - no time
            - Has end:
                - has time
                - no time

            Returns: key value dictionaries of row-id and start date, row-id and end date with the purpose of making looking up these values more simple for other functions. 
            {Id: start, Id: start}
            {Id: end, Id: end}
            """
            start_dates = {}
            end_dates = {}

            for i in range(self.data_len):
                record_id, row_data = self.current_row(i)

                try: #evaluate rows where date exists
                    raw_start = row_data['properties'][self.field]['date']['start']
                    raw_end = row_data['properties'][self.field]['date']['end']
                    date_pattern = '%Y-%m-%d'
                    date_time_pattern = '%Y-%m-%dT%H:%M:%S.%f%z'
                    
                    if (raw_end == None): #no end date

                        if re.match(r'.*T.*', raw_start): #has time, use date_time_pattern
                            formatted_start = dt.strptime(raw_start, date_time_pattern)
                            formatted_end = None

                        else: #has no time, use date_pattern
                            formatted_start = dt.strptime(raw_start, date_pattern)
                            formatted_end = None

                    elif (raw_end != None): #has end date

                        if re.match(r'.*T.*', raw_start): #has time, use date_time_pattern
                            formatted_start = dt.strptime(raw_start, date_time_pattern)
                            formatted_end = dt.strptime(raw_end, date_time_pattern)

                        else:  #has no time, use date_pattern
                            formatted_start = dt.strptime(raw_start, date_pattern)
                            formatted_end = dt.strptime(raw_end, date_pattern)

                    start_dates[record_id] = formatted_start
                    end_dates[record_id] = formatted_end

                except KeyError: #if doesn't exist, write None
                    
                    start_dates[record_id] = None
                    end_dates[record_id] = None

            return start_dates, end_dates

        def relation(self):
            """
            Extracts multiple relations from a given field
            Returns as a dict w/ row id as key and list of relations

            {record_id: [relation, relation, relation]}
            """
            relation_dict = {}

            for i in range(self.data_len):
                record_id, row_data = self.current_row(i)

                relation_list_raw = row_data['properties'][self.field]['relation']
                relations_extracted = []

                for item in relation_list_raw:
                    #append each relation value to list
                    relation_id = item['id']
                    relations_extracted.append(relation_id)

                #arrange into dictionary
                relation_dict[record_id] = relations_extracted

            return relation_dict

        def text(self):
            """
            Extract data from text type fields 
            Returns as a dict w/ row id as key and raw title text
            If list is empty will throw an index error
            """

            text_dict = {}

            for i in range(self.data_len):
                record_id, row_data = self.current_row(i)
                
                try:
                    text_extracted = row_data['properties'][self.field]['text'][0]['plain_text']

                except IndexError: #skips rows w/ empty lists
                    text_extracted = None
            
                text_dict[record_id] = text_extracted

            return text_dict

        def rich_text(self):
            """
            Extract data from text type fields 
            Returns as a dict w/ row id as key and raw title text
            If list is empty will throw an index error
            """

            text_dict = {}

            for i in range(self.data_len):
                record_id, row_data = self.current_row(i)
                
                try:
                    text_extracted = row_data['properties'][self.field]['rich_text'][0]['plain_text']

                except IndexError: #skips rows w/ empty lists
                    text_extracted = None
                
                text_dict[record_id] = text_extracted

            return text_dict
        
        def title(self):
            """
            Extract data from title type fields
            Returns as a dict w/ row id as key and raw title text
            """

            title_dict = {}

            for i in range(self.data_len):
                record_id, row_data = self.current_row(i)
                
                try:
                    text_extracted = row_data['properties'][self.field]['title'][0]['plain_text']

                except IndexError: #skips rows w/ empty lists
                    text_extracted = None
            
                title_dict[record_id] = text_extracted

            return title_dict

        def select(self):
            """
            Extract data from select type fields. 
            Returns as a dict w/ row id as key and raw text. 
            If details aren't provided for a select field, it will not appear in json at all.
            """

            select_dict = {}

            for i in range(self.data_len):
                record_id, row_data = self.current_row(i)
                
                try:
                    text_extracted = row_data['properties'][self.field]['select']['name']

                except KeyError: #does not exist if field is empty in UI (returns KeyError)
                    text_extracted = None
            
                select_dict[record_id] = text_extracted

            return select_dict

        def checkbox(self):

            """
            Extract data from checkbox. 
            Data returned from API is boolean True / False.
            """

            check_dict = {}

            for i in range(self.data_len):
                record_id, row_data = self.current_row(i)
                
                try:
                    text_extracted = row_data['properties'][self.field]['checkbox']

                except IndexError: #technically always seems to return a boolean True / False so this error shouldn't raise
                    text_extracted = None
            
                check_dict[record_id] = text_extracted

            return check_dict
