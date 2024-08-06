from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView
from django.conf import settings
from movies.models import Filmwork, PersonFilmwork


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']

    def get_queryset(self):
        queryset = Filmwork.objects.prefetch_related('genres', 'persons').order_by('id')
        return queryset.values()\
            .annotate(genres=ArrayAgg('genres__name', distinct=True))\
            .annotate(actors=ArrayAgg('persons__full_name', filter=Q(personfilmwork__role=PersonFilmwork.RoleType.ACTOR), distinct=True))\
            .annotate(directors=ArrayAgg('persons__full_name', filter=Q(personfilmwork__role=PersonFilmwork.RoleType.DIRECTOR), distinct=True))\
            .annotate(writers=ArrayAgg('persons__full_name', filter=Q(personfilmwork__role=PersonFilmwork.RoleType.WRITER), distinct=True))\
            .values('id', 'title', 'description', 'creation_date', 'rating', 'type', 'genres', 'actors', 'directors', 'writers')

    def render_to_response(self, context):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = settings.PAGES

    def get_context_data(self):
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset,
            self.paginate_by
        )
        context = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': page.number - 1 if page.has_previous() else page.number,
            'next': page.number + 1 if page.has_next() else page.number,
            'results': list(queryset),
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        queryset = self.get_queryset().filter(id=pk)
        context = list(queryset)
        return context[0]
