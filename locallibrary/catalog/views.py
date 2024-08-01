import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Book, Author, BookInstance, Genre
from django.views import generic
from .constants import ITEMS_PER_PAGE, BOOKINSTANCE_LIST_BORROWED_USER_PER_PAGE
from django.contrib.auth.mixins import LoginRequiredMixin
from catalog.forms import RenewBookForm
from django.contrib.auth.mixins import PermissionRequiredMixin


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
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
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

def book_detail_view(request, pk):
    # Lay thong tin cuon sach tu csdl dua vao id, neu khong ton tai thi tra ve 404
    book = get_object_or_404(Book, pk=pk)
    # Sap xep genre theo alphabet
    genres = book.genre.all().order_by('name')
    # Sap xep cac ban copy theo ngay tao
    book_instances = BookInstance.objects.all().order_by('creation_date')
    return render(request, 'catalog/book_detail.html', {'book': book, 'genres': genres, 'book_instances': book_instances})

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.count()
    num_instances = BookInstance.objects.count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact=BookInstance.BookStatus.AVAILABLE).count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    paginate_by = ITEMS_PER_PAGE

    # select_related su dung cho quan he one-to-one hoac many-to-one
    # prefetch_related su dung cho quan he many-to-many hoac reverse many-to-one (truong hop nguoc lai cua ForeignKey)
    def get_queryset(self):
        # Su dung select_related de lay thong tin cua author cung luc khi query book
        return Book.objects.select_related('author').all()
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['some_data'] = 'This is just some data'
        return context

class BookDetailView(generic.DetailView):
    model = Book

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = BOOKINSTANCE_LIST_BORROWED_USER_PER_PAGE

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .select_related('book')
            .order_by('due_back')
        )

class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'all-borrowed.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back').select_related('borrower')
    
class AuthorListView(generic.ListView):
    """Generic class-based list view for a list of authors."""
    model = Author
    paginate_by = ITEMS_PER_PAGE

class AuthorDetailView(generic.DetailView):
    """Generic class-based detail view for an author."""
    model = Author

class AuthorCreate(CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/11/2023'}

class AuthorUpdate(UpdateView):
    model = Author
    # Not recommended (potential security issue if more fields added)
    fields = '__all__'

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
