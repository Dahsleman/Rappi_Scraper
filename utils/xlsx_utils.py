import pandas as pd

class XlsxUtils:
    @staticmethod
    def update_xlsx_with_json(df_products, df_address, xlsx_file, df_errors = None, headers_products=None):
        print('UPDATING EXCEL FILE')
        
        sheet_products_name = 'Products'
        sheet_errors_name = 'Erros'

        try:
            with pd.ExcelWriter(xlsx_file, engine='openpyxl') as writer:
                
                if headers_products is not None:
                    df_products.to_excel(writer, sheet_name=sheet_products_name, header=headers_products, index=False)
                    df_products.to_excel(writer, sheet_name=sheet_products_name, header=False, startrow=1, index=False)
                else:
                    df_products.to_excel(writer, sheet_name=sheet_products_name, index=False)
                print(f"Sheet {sheet_products_name} updated.")

                df_address.to_excel(writer, sheet_name='Address', index=False)
                print(f"Sheet Address updated.")

                if df_errors is not None:
                    df_errors.to_excel(writer, sheet_name=sheet_errors_name, index=False)
                    
                    print(f"Sheet {sheet_errors_name} updated.")
        except Exception as error:
            print(error)
            exit()

    # params
    #   xlsx_file_path (ex: "dictionary.xlsx"),
    #   param sheet_name (ex: "DIC_COMPLEMENT_WORDS")
    @staticmethod
    def read_xlsx(xlsx_file_path, sheet_name):
        try:
            return pd.read_excel(xlsx_file_path, sheet_name=sheet_name, dtype=str)
        except Exception as error:
            print(error)
            print(f'ERROR: Confira se o caminho e o arquivo estao corretos')
            return None

    @staticmethod
    def get_columns_by_key(xlsx_file, key):
        if xlsx_file is None:
            return None
        
        key = key.lower()
        if (key in xlsx_file.columns):
            columns_list = xlsx_file[key].tolist()
            return list(filter(lambda s: isinstance(s, str) and s, columns_list))

        return None