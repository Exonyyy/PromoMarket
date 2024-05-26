from settings import PRODUCT_LIST_PAGE
from math import ceil


def sort_data_by_market(data):
    market_data = dict()
    product_num = 1
    for product in data:
        if product[3] in market_data.keys():
            market_data[product[3]].append((product_num, product[0], product[1], product[2]))
        else:
            market_data[product[3]] = []
            market_data[product[3]].append((product_num, product[0], product[1], product[2]))
        product_num += 1
    return market_data


def get_table(data, page=1):
    market_data = sort_data_by_market(data[page*PRODUCT_LIST_PAGE-30:page*PRODUCT_LIST_PAGE+1])
    last_page = ceil(len(data)/PRODUCT_LIST_PAGE)
    data_text = ""
    for market, products in market_data.items():
        data_text += f"{market.replace("_", " ").title()}\n"
        for product in products:
            product_cost = product[2] if int(product[2]) != product[2] else int(product[2])
            data_text += f"{product[0]}. {product[1]}, {product_cost} руб/шт, {product[3]}шт ост.\n"
        data_text += "\n"
    return data_text, last_page

