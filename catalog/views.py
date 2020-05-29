import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
# from django.core.exceptions import PermissionDenied
from django.views import generic
from .models import Book, Author, BookInstance, Genre
from .forms import RenewBookForm


# View (function-based) -> using @login_required to authencitaion views
@login_required
# @permission_required('catalog.can_mark_returned')
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
class BookListView(PermissionRequiredMixin, generic.ListView):
    model = Book  # Your model
    paginate_by = 2
    permission_required = ('catalog.view_book')

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


class BookDetailView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    model = Book
    template_name = 'books/book_detail.html'
    permission_required = ('catalog.view_book')

    def book_detail_view(request, primary_key):
        try:
            book = Book.objects.get(pk=primary_key)
        except Book.DoesNotExist:
            raise get_object_or_404('Book Does Not Exist')

        return render(request, template_name, context={'book': book})


class AuthorListView(PermissionRequiredMixin, generic.ListView):
    model = Author
    paginate_by = 2
    raise_exception = True
    template_name = 'authors/author_list.html'
    permission_required = ('catalog.view_author')

    def get_queryset(self):
        # if not request.user.has_perm(self.permission_required):
        # raise PermissionDenied(self.get_permission_denied_message())

        return Author.objects.all()

    def get_context_data(self, **kwargs):
        context = super(AuthorListView, self).get_context_data(**kwargs)
        return context


class AuthorDetailView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    model = Author
    template_name = 'authors/author_detail.html'
    permission_required = ('catalog.view_author')

    def author_detail_view(request, primary_key):
        try:
            author = Author.objects.get(pk=primary_key)
        except Author.DoesNotExist:
            raise get_object_or_404('Author Does Not Exist')

        return render(request, template_name, context={'author': author})


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'bookinstance/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'bookinstance/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # Handle POST Request Form Data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding)
        form = RenewBookForm(request.POST)

        # Check if the code is valid
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance
    }

    return render(request, 'bookinstance/book_renew_librarian.html', context)
