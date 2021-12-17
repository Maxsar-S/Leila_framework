from datetime import date
from views import Index, HistoryAG, HistoryAE, HistoryAR, \
    ArticlesList, CreateArticle, CreateCategory, CategoryList, CopyArticle


def secret_front(request):
    request['data'] = date.today()


def other_front(request):
    request['key'] = 'key'


fronts = [secret_front, other_front]

# routes = {
#     '/': Index(),
#     '/greece/': HistoryAG(),
#     '/rome/': HistoryAR(),
#     '/egypt/': HistoryAE(),
#     '/article-list/': ArticlesList(),
#     '/create-article/': CreateArticle(),
#     '/create-category/': CreateCategory(),
#     '/category-list/': CategoryList(),
#     '/copy-article/': CopyArticle(),
# }
