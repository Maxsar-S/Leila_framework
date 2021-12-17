from leila_framework.templator import render
from patterns.creational_patterns import Engine, Logger, MapperRegistry
from patterns.structural_patterns import AppRoute, Debug
from patterns.behavioral_patterns import EmailNotifier, SmsNotifier, \
    TemplateView, ListView, CreateView, BaseSerializer
from patterns.architectural_system_pattern_unit_of_work import UnitOfWork

site = Engine()
logger = Logger('main')
email_notifier = EmailNotifier()
sms_notifier = SmsNotifier()
UnitOfWork.new_current()
UnitOfWork.get_current().set_mapper_registry(MapperRegistry)

routes = {}


@AppRoute(routes=routes, url='/')
class Index:
    @Debug(name='Index')
    def __call__(self, request):
        return '200 OK', render('index.html', objects_list=site.categories)


@AppRoute(routes=routes, url='/greece/')
class HistoryAG:
    @Debug(name='Greece')
    def __call__(self, request):
        return '200 OK', 'history of Ancient Greece'


@AppRoute(routes=routes, url='/egypt/')
class HistoryAE:
    @Debug(name='Egypt')
    def __call__(self, request):
        return '200 OK', 'history of Ancient Rome'


@AppRoute(routes=routes, url='/rome/')
class HistoryAR:
    @Debug(name='Rome')
    def __call__(self, request):
        return '200 OK', 'history of Ancient Egypt'


class NotFound404:
    @Debug(name='404')
    def __call__(self, request):
        return '404 WHAT', '404 PAGE Not Found'


@AppRoute(routes=routes, url='/article-list/')
class ArticlesList:
    @Debug(name='ArticleList')
    def __call__(self, request):
        logger.log('Список статей')
        try:
            category = site.find_category_by_id(int(request['request_params']['id']))
            return '200 OK', render('article_list.html', objects_list=category.articles, name=category.name,
                                    id=category.id)
        except KeyError:
            return '200 OK', 'No articles have been added yet'


@AppRoute(routes=routes, url='/create-article/')
class CreateArticle:
    category_id = -1

    @Debug(name='CreateArticle')
    def __call__(self, request):
        if request['method'] == 'POST':
            data = request['data']
            name = data['name']
            name = site.decode_value(name)

            category = None
            if self.category_id != -1:
                category = site.find_category_by_id(int(self.category_id))

                article = site.create_article('record', name, category)
                site.articles.append(article)

            return '200 OK', render('article_list.html', objects_list=category.articles,
                                    name=category.name, id=category.id)

        else:
            try:
                self.category_id = int(request['request_params']['id'])
                category = site.find_category_by_id(int(self.category_id))

                return '200 OK', render('create_article.html', name=category.name, id=category.id)
            except KeyError:
                return '200 OK', 'No categories have been added yet'


@AppRoute(routes=routes, url='/create-category/')
class CreateCategory:

    @Debug(name='CreateCategory')
    def __call__(self, request):

        if request['method'] == 'POST':
            print(request)
            data = request['data']
            name = data['name']
            name = site.decode_value(name)
            category_id = data.get('category_id')

            category = None
            if category_id:
                category = site.find_category_by_id(int(category_id))

            new_category = site.create_category(name, category)

            site.categories.append(new_category)

            return '200 OK', render('index.html', objects_list=site.categories)
        else:
            categories = site.categories
            return '200 OK', render('create_category.html', categories=categories)


@AppRoute(routes=routes, url='/category-list/')
class CategoryList:
    @Debug(name='CategoryList')
    def __call__(self, request):
        logger.log('Список категорий')
        return '200 OK', render('category_list.html', objects_list=site.categories)


@AppRoute(routes=routes, url='/copy-article/')
class CopyArticle:
    @Debug(name='CopyArticle')
    def __call__(self, request):
        request_params = request['request_params']
        try:
            name = request_params['name']
            old_article = site.get_article(name)
            if old_article:
                new_name = f'copy_{name}'
                new_article = old_article.clone()
                new_article.name = new_name
                site.articles.append(new_article)

            return '200 OK', render('article_list.html', objects_list=site.articles)
        except KeyError:
            return '200 OK', 'No articles have been added yet'


@AppRoute(routes=routes, url='/readers-list/')
class ReaderListView(ListView):
    template_name = 'readers_list.html'

    def get_queryset(self):
        mapper = MapperRegistry.get_current_mapper('reader')
        return mapper.all()


@AppRoute(routes=routes, url='/create-reader/')
class ReaderCreateView(CreateView):
    template_name = 'create_reader.html'

    def create_obj(self, data: dict):
        name = data['name']
        name = site.decode_value(name)
        new_obj = site.create_user('reader', name)
        site.readers.append(new_obj)
        new_obj.mark_new()
        UnitOfWork.get_current().commit()


@AppRoute(routes=routes, url='/add-reader/')
class AddReaderByArticleCreateView(CreateView):
    template_name = 'add_reader.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['articles'] = site.articles
        context['readers'] = site.readers
        return context

    def create_obj(self, data: dict):
        article_name = data['article_name']
        article_name = site.decode_value(article_name)
        article = site.get_article(article_name)
        reader_name = data['reader_name']
        reader_name = site.decode_value(reader_name)
        reader = site.get_reader(reader_name)
        article.add_reader(reader)


@AppRoute(routes=routes, url='/api/')
class ArticleApi:
    @Debug(name='ArticleApi')
    def __call__(self, request):
        return '200 OK', BaseSerializer(site.articles).save()
