from ast import literal_eval
import pandas as pd

class InputSettings:
# Load the Excel Workbook
    workbook_path = './Workbook.xlsx'

    # Read sheets into dataframes
    df_name = pd.read_excel(workbook_path, sheet_name='name')
    df_address = pd.read_excel(workbook_path, sheet_name='address')
    df_query = pd.read_excel(workbook_path, sheet_name='query')
    df_spreadsheet_id = pd.read_excel(workbook_path, sheet_name='spreadsheet_id')

    # print(df_address)
    # print(df_query)

    # Create CLIENTS dynamically
    CLIENTS = []
    for i in df_name.index:
        # Convert the string-formatted 'Query' to an actual dictionary
        cell_content = df_query.iloc[i]['Query']  # <-- New line
        query_dict = {(cell_content, "kg"): ()}   # <-- Changed this line
        # print(query_dict)
        client_dict = {
            "__NAME__": df_name.iloc[i]['Name'],
            "__ADDRESS__": df_address.iloc[i]['Address'],
            "__QUERY__": query_dict,  # <-- Changed this line
            "__SPREADSHEET_ID__": df_spreadsheet_id.iloc[i]['Spreadsheet_ID']
        }
        CLIENTS.append(client_dict)

    DICTIONARY_FILE_PATH = 'G:/My Drive/kompru/dictionary.xlsx'
    DIRECTORY_PATH = "/Users/athos/Library/CloudStorage/GoogleDrive-athos@kompru.com/My Drive/06 Code/Barra-de-busca-para-itens-MVP/rappi-scrapper/"

    # 1 HOUR = 60 * 60
    AUTO_SCRIPT_SCHEDULER_TIME = 1

    # True  -> Save oducts-out-stock = False in .xlsx file
    ONLY_AVAILABLE_PRODUCTS = False

    # True  -> Save only match-search-term? = True in .xlsx file
    ONLY_MATCH_SEARCH_TERM_PRODUCTS = False

    # True  -> Save only product-input-price != incompativel in .xlsx file
    ONLY_COMPATIBLE_PRICES_PRODUCTS = False
    
    # Excel Header columns
    EXCEL_HEADER = ['k collected-at',         'k term',                   'k unit-input', 
                    'store-id',               'store-type',               'product-id',
                    'master-product-id',      'product-price',            'product-real-price',
                    'product-unit',           'k product-size',           'k unit-input-size',
                    'k product-input-unit',   'k product-input-price',    'k match-unit-input?',
                    'product-name',           'k term-in-product-name?',  'product-out-stock',
                    'step-quantity-in-grams']