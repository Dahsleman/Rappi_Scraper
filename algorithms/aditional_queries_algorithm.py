from input_settings import InputSettings
from utils.xlsx_utils import XlsxUtils

class AditionalQueriesAlgorithm:
    @staticmethod
    # param
    #   query is a tuple (arr, arr)
    def get_aditional_queries(query, keywords, file_sheet_synonym_words):
        search_key = query[0]
        unit = query[1]
        new_list = list()

        columns = XlsxUtils.get_columns_by_key(file_sheet_synonym_words, search_key)
        if columns is not None:
            for col in columns:
                new_list.append({(col, unit):keywords})

        return new_list

    @staticmethod
    def addAditionalQueries(queries, original_queries_dic):
        file_path = InputSettings.DICTIONARY_FILE_PATH
        file_sheet_synonym_words = XlsxUtils.read_xlsx(file_path, "DICTIONARY_SYNONYM_WORDS")
        _aditional_queries = list()
        _remove_queries = list()

        for query, keywords in queries.items():
            _qies = AditionalQueriesAlgorithm.get_aditional_queries(
                query,
                keywords,
                file_sheet_synonym_words)
            if _qies is not None and len(_qies) > 0:
                for add_q_val in _qies:
                    _query, _keywords = list(add_q_val.keys())[0]
                    original_queries_dic[_query] = query[0]
                _aditional_queries = _aditional_queries + _qies
                _remove_queries.append(query)

        for add_q in _aditional_queries:
            for add_q_val in add_q:
                queries[add_q_val] = add_q[add_q_val]
        for remove_q in _remove_queries:
            queries.pop(remove_q)
