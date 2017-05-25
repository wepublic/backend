from rest_framework.pagination import PageNumberPagination


class NewestQuestionsSetPagination(PageNumberPagination):
    page_size = 50
