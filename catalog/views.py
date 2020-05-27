from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from .models import Book, Author, BookInstance, Genre


# View (function-based) -> using @login_required to authencitaion views
@login_required
def index(request):
    """ View function for home page of site. """
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(
        status__exact='a').count()

    # The 'all()' is implied by default
    num_authors = Author.objects.count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {'num_books': num_books, 'num_instances': num_instances,
               'num_instances_available': num_instances_available,
               'num_authors': num_authors, 'num_visits': num_visits}

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context)


# LoginRequiredMixin -> handling authentication views
class BookListView(LoginRequiredMixin, generic.ListView):
    model = Book  # Your model
    paginate_by = 2

    # your own name for the list as a template variable
    # context_object_name = 'book_list'

    # queryset = Book.objects.all()

    # Specify your own template name/location
    template_name = 'books/book_list.html'

    # Overriding methods in class-based views
    # Overriding variable queryset
    def get_queryset(self):
        return Book.objects.all()

    # Overriding variable context_object_name
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        # context['some_data'] = 'This is just some data'
        return context


class BookDetailView(generic.DetailView):
    model = Book
    template_name = 'books/book_detail.html'

    def book_detail_view(request, primary_key):
        try:
            book = Book.objects.get(pk=primary_key)
        except Book.DoesNotExist:
            raise get_object_or_404('Book Does Not Exist')

        return render(request, template_name, context={'book': book})


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 2
    template_name = 'authors/author_list.html'

    def get_queryset(self):
        return Author.objects.all()

    def get_context_data(self, **kwargs):
        context = super(AuthorListView, self).get_context_data(**kwargs)
        return context


class AuthorDetailView(generic.DetailView):
    model = Author
    template_name = 'authors/author_detail.html'

    def author_detail_view(request, primary_key):
        try:
            author = Author.objects.get(pk=primary_key)
        except Author.DoesNotExist:
            raise get_object_or_404('Author Does Not Exist')

        return render(request, template_name, context={'author': author})
