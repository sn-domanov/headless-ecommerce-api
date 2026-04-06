from rest_framework.pagination import PageNumberPagination


# TODO Consider using CursorPagination on large datasets
class StandardPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    page_size = 10
    max_page_size = 50
