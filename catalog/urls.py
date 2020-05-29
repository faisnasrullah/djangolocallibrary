from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('book/', views.BookListView.as_view(), name='books'),
    # path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    re_path(r'^book/(?P<pk>\d+)$',
            views.BookDetailView.as_view(), name='book-detail'),

    path('author/', views.AuthorListView.as_view(), name='authors'),
    re_path(r'^author/(?P<pk>\d+)$',
            views.AuthorDetailView.as_view(), name='author-detail'),

    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    path('borrowed/', views.LoanedBooksAllListView.as_view(), name='all-borrowed'),

    path('book/<uuid:pk>/renew/', views.renew_book_librarian,
         name='renew-book-librarian'),
]
