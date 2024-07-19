from django.shortcuts import render

from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.shortcuts import get_object_or_404
from .constants import ITEMS_PER_PAGE  

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

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
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


