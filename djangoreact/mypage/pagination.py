from rest_framework.pagination import PageNumberPagination

class MyContentsPage(PageNumberPagination):
    page_size = 5