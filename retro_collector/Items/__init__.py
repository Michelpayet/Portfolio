import datetime
import jsonpickle
import os
from typing import List


class Item:
    ITEMS: List = []

    def __init__(self, title: str, type: str, description: str, condition: str, dom: datetime.date,
                 dad: datetime.date):
        self.title: str = title
        self.type: str = type
        self.description: str = description
        self.condition: str = condition
        self.dom: datetime.date = dom
        self.dad: datetime.date = dad
        Item.ITEMS.append(self)

    @staticmethod
    def save_to_file() -> None:
        json_object = jsonpickle.encode(Item.ITEMS, unpicklable=False)
        with open('collection.json', 'w') as outfile:
            outfile.write(json_object)

    @staticmethod
    def load_from_file() -> None:
        Item.ITEMS.clear()

        if not os.path.isfile('collection.json') or not os.path.getsize('collection.json') > 0:
            return

        with open('collection.json') as infile:
            json_object = infile.read()
            list_of_dict = jsonpickle.decode(json_object)
            for item in list_of_dict:
                Item(
                    item['title'],
                    item['type'],
                    item['description'],
                    item['condition'],
                    datetime.datetime.strptime(item['dom'], '%Y-%m-%d').date(),
                    datetime.datetime.strptime(item['dad'], '%Y-%m-%d').date()
                )


