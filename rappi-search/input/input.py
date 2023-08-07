"""INPUTS"""

"""
Colocar o endereco igual no google maps
Exemplo:
    address = 'R. Jandiatuba, 74 - Buritis, Belo Horizonte - MG, 30493-135'

Colocar as querys dentro da lista igual exemplo.
Exemplo:
    querys = {
        ("leite","l"):('zero lactose', 'sem lactose', 'lacfree'),
    }

sendo: 
    "leite" a query

    "l" a unidade (A unidade tem que ser uma das a seguir: ml, kg, gr, l ou und)

    'zero lactose', 'sem lactose', 'lacfree' as keywords (Quando nao quiser usar keywords so lancar a "tupla" vazia)

ex:
    querys = {
        ("leite","l"):(),
    }
"""
client = 'Luis'

address = 'R. Prof. Baroni, 190 - 101 - Gutierrez, Belo Horizonte - MG, 30441-180'

querys = {
    ("LEITE INTEGRAL","L"):('instantaneo','bufala','lactose','lacfree','condensado','desnatado','semidesnatado','creme')
}



