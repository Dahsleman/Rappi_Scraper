from utils.rappi_product_utils import RappiProductUtils
from input_settings import InputSettings
from utils.xlsx_utils import XlsxUtils
import pandas as pd
import json
import os

class FileGenerator:
    @staticmethod
    def generateFiles(products_list, clientDetails, new_error_list = None):
        directory_path = InputSettings.DIRECTORY_PATH
        address = clientDetails["__ADDRESS__"]
        client = clientDetails["__NAME__"]
        headers_products = InputSettings.EXCEL_HEADER

        try:
            os.mkdir(f'{directory_path}/{client}')
            print(f'Directory {directory_path}/{client} created')
        except FileExistsError:
            print(f'Directory {directory_path}/{client} already exist')

        file_path = f'{directory_path}/{client}/{client}'
        file_path_errors = f'{directory_path}/{client}/{client}_errors'

        if new_error_list is not None:
            if os.path.isfile(f'{file_path}.json'):
                # Update json_file of products.
                with open(f'{file_path}.json', 'r') as json_file:
                    existing_data = json.load(json_file)
                    json_file.close()

                if len(existing_data) > 0:
                    if type(existing_data[0]) is dict:
                        for index, data in enumerate(existing_data):
                            existing_data[index] = list(RappiProductUtils.setupProductObjectWithHeader(data).values())
                for item in products_list:
                    existing_data.append(list(item.values()))
                with open(f'{file_path}.json', 'w') as fp:
                    json.dump(existing_data, fp, indent=1)
                    fp.close()
            else:
                _products_list = []
                for product in products_list:
                    _products_list.append(list(product.values()))
                # Create json_file of products.
                with open(f'{file_path}.json', 'w') as fp:
                    json.dump(_products_list, fp, indent=1)
                    fp.close()

            if os.path.isfile(f'{file_path_errors}.json'):
                # Update json_file of errors.
                with open(f'{file_path_errors}.json', 'r') as json_file:
                    existing_data = json.load(json_file)
                    json_file.close()
                for item in new_error_list:
                    existing_data.append(item)
                with open(f'{file_path_errors}.json', 'w') as fp:
                    json.dump(existing_data, fp, separators=(',', ':'))
            else:
                # Create json_file of errors.
                with open(f'{file_path_errors}.json', 'w') as fp:
                    json.dump(new_error_list, fp, separators=(',', ':'))     
        else:
            _products_list = []
            for product in products_list:
                _products_list.append(product)
            with open(f'{file_path}.json', 'w') as fp:
                    json.dump(_products_list, fp, indent=1)
                    fp.close()

        json_file = f'{file_path}.json'
        json_file_errors = f'{file_path_errors}.json'
        xlsx_file = f'{file_path}.xlsx'
        mvp_xlsx_file = f'{file_path}_mvp.xlsx'

        if not os.path.isfile(json_file):
            print('There is no json_file, please run auto_script.py with right InputSettings.DIRECTORY_PATH')
        else:
            print(f'Openning ${json_file}')
            # Create a new dataframe with the Products
            df_products = pd.read_json(json_file, convert_axes=False)

            # Create a new dataframe with the address
            df_address = pd.DataFrame({'Address': [address]})

            if new_error_list is not None:
                # Create a new dataframe with the Errors
                print(f'Openning ${json_file_errors}')
                df_errors = pd.read_json(json_file_errors)

            if new_error_list is not None:
                XlsxUtils.update_xlsx_with_json(df_products, df_address, df_errors, xlsx_file, headers_products)
            else:
                XlsxUtils.update_xlsx_with_json(df_products, df_address, mvp_xlsx_file)