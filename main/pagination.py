from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class PageNumberPaginationPost(PageNumberPagination):
    page_size = 5
    max_page_size = 100

    def get_paginated_response(self, data):
        # return super().get_paginated_response(data)
        # print("print data in paginated response", data)
        return Response({
            'count': self.page.paginator.count,
            # 'page_size': self.get_page_size(),
            # 'current_page': self.get_page_number(),
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'data': data
        })