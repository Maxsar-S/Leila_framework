import copy
import quopri
import sqlite3

from .behavioral_patterns import ConsoleWriter, Subject
from .architectural_system_pattern_unit_of_work import DomainObject


class User:
    def __init__(self, name):
        self.name = name


class Author(User):
    pass


class Reader(User, DomainObject):
    def __init__(self, name):
        self.articles = []
        super().__init__(name)


# порождающий паттерн Абстрактная фабрика
class UserFactory:
    types = {
        'reader': Reader,
        'author': Author
    }

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_):
        return cls.types[type_]()


# порождающий паттерн Прототип - статья
class ArticlePrototype:
    # прототип курсов обучения

    def clone(self):
        return copy.deepcopy(self)


class Article(ArticlePrototype, Subject):

    def __init__(self, name, category):
        self.name = name
        self.category = category
        self.category.articles.append(self)
        self.readers = []
        super().__init__()

    def __getitem__(self, item):
        return self.readers[item]

    def add_reader(self, reader: Reader):
        self.readers.append(reader)
        reader.articles.append(self)
        self.notify()


class ApprovedArticle(Article):
    pass


class UnapprovedArticle(Article):
    pass


class Category:
    auto_id = 0

    def __init__(self, name, category):
        self.id = Category.auto_id
        Category.auto_id += 1
        self.name = name
        self.category = category
        self.articles = []

    def article_count(self):
        result = len(self.articles)
        if self.category:
            result += self.category.article_count()
        return result


# порождающий паттерн Абстрактная фабрика
class ArticleFactory:
    types = {
        'approved': ApprovedArticle,
        'unapproved': UnapprovedArticle
    }

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_, name, category):
        return cls.types[type_](name, category)


# Основной интерфейс проекта
class Engine:
    def __init__(self):
        self.authors = []
        self.readers = []
        self.articles = []
        self.categories = []

    @staticmethod
    def create_user(type_):
        return UserFactory.create(type_)

    @staticmethod
    def create_category(name, category=None):
        return Category(name, category)

    def find_category_by_id(self, id):
        for item in self.categories:
            print('item', item.id)
            if item.id == id:
                return item
        raise Exception(f'Нет категории с id = {id}')

    @staticmethod
    def create_article(type_, name, category):
        return ArticleFactory.create(type_, name, category)

    def get_article(self, name):
        for item in self.articles:
            if item.name == name:
                return item
        return None

    def get_reader(self, name) -> Reader:
        for item in self.readers:
            if item.name == name:
                return item

    @staticmethod
    def decode_value(val):
        val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
        val_decode_str = quopri.decodestring(val_b)
        return val_decode_str.decode('UTF-8')


# порождающий паттерн Синглтон
class SingletonByName(type):

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = {}

    def __call__(cls, *args, **kwargs):
        if args:
            name = args[0]
        if kwargs:
            name = kwargs['name']

        if name in cls.__instance:
            return cls.__instance[name]
        else:
            cls.__instance[name] = super().__call__(*args, **kwargs)
            return cls.__instance[name]


class Logger(metaclass=SingletonByName):

    def __init__(self, name, writer=ConsoleWriter()):
        self.name = name
        self.writer = writer

    def log(self, text):
        text = f'log---> {text}'
        self.writer.write(text)


class ReaderMapper:

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.tablename = 'reader'

    def all(self):
        statement = f'SELECT * from {self.tablename}'
        self.cursor.execute(statement)
        result = []
        for item in self.cursor.fetchall():
            id, name = item
            reader = Reader(name)
            reader.id = id
            result.append(reader)
        return result

    def find_by_id(self, id):
        statement = f"SELECT id, name FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (id,))
        result = self.cursor.fetchone()
        if result:
            return Reader(*result)
        else:
            raise RecordNotFoundException(f'record with id={id} not found')

    def insert(self, obj):
        statement = f"INSERT INTO {self.tablename} (name) VALUES (?)"
        self.cursor.execute(statement, (obj.name,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def update(self, obj):
        statement = f"UPDATE {self.tablename} SET name=? WHERE id=?"
        self.cursor.execute(statement, (obj.name, obj.id))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbUpdateException(e.args)

    def delete(self, obj):
        statement = f"DELETE FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbDeleteException(e.args)


connection = sqlite3.connect('patterns.sqlite')


class MapperRegistry:
    mappers = {
        'reader': ReaderMapper,
    }

    @staticmethod
    def get_mapper(obj):
        if isinstance(obj, Reader):
            return ReaderMapper(connection)

    @staticmethod
    def get_current_mapper(name):
        return MapperRegistry.mappers[name](connection)


class DbCommitException(Exception):
    def __init__(self, message):
        super().__init__(f'Db commit error: {message}')


class DbUpdateException(Exception):
    def __init__(self, message):
        super().__init__(f'Db update error: {message}')


class DbDeleteException(Exception):
    def __init__(self, message):
        super().__init__(f'Db delete error: {message}')


class RecordNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(f'Record not found: {message}')
