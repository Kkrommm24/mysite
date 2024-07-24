from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _ # Update i18n standard
import uuid

class Genre(models.Model):
    """Model representing a book genre."""
    name = models.CharField(max_length=200, help_text=_('Enter a book genre (e.g. Science Fiction)'))

    def __str__(self):
        """String for representing the Model object."""
        return self.name

class Book(models.Model):
    """Model representing a book (but not a specific copy of a book)."""
    title = models.CharField(max_length=200)
    
    # CAC GIA TRI KHAC CUA ON_DELETE:
    # - CASCADE: Xoa tat ca cac ban ghi lien quan khi ban ghi doi tuong duoc tham chieu bi xoa.
    # - PROTECT: Khong cho xoa ban ghi neu co ban ghi lien quan toi no. Neu co gang xoa, Django se nem ra mot loi ProtectedError.
    # - SET_NULL: Dat truong quan he tren doi tuong lien quan la NULL khi ban ghi doi tuong duoc tham chieu bi xoa. 
    # - SET_DEFAULT: Dat truong quan he tren doi tuong lien quan la gia tri mac dinh khi ban ghi doi tuong duoc tham chieu bi xoa.
    # - SET(): Dat truong quan he tren doi tuong lien quan la gia tri chi dinh khi ban ghi doi tuong duoc tham chieu bi xoa.
    # - DO_NOTHING: Khong lam gi ca. Neu co gang xoa ban ghi, co the bi pha huy cac rang buoc khoa ngoai cua CSDL.
    # - RESTRICT: Giong nhu PROTECT. Nhung cho phep xoa doi tuong neu viec do khong vi pham rang buoc khoa ngoai. trong mot Transaction.

    author = models.ForeignKey('Author', on_delete=models.RESTRICT, null=True)

    summary = models.TextField(max_length=1000, help_text=_("Enter a brief description of the book"))
    isbn = models.CharField(_('ISBN'), max_length=13,
                            unique=True,
                            help_text=_('13 Character <a href="https://www.isbn-international.org/content/what-isbn'
                                        '">ISBN number</a>'))


    genre = models.ManyToManyField(Genre, help_text=_("Select a genre for this book"))

    # Dinh nghia cac mot object cua model duoc chuyen thanh chuoi, o day phuong thuc tra ve gia tri dang chuoi cua truong title
    def __str__(self):
        """String for representing the Model object."""
        return self.title
    # Dinh nghia duong dan tuyet doi den mot chi tiet ban ghi cho cuon sach nay, o day method su dung reverse() de tao URL dua tren 
    # pattern 'book-detail' va tham so la id cua ban ghi
    def get_absolute_url(self):
        """Returns the URL to access a detail record for this book."""
        return reverse('book-detail', args=[str(self.id)])

class BookInstance(models.Model):

    """Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text=_("Unique ID for this particular book across whole library"))
    book = models.ForeignKey('Book', on_delete=models.RESTRICT)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='m',
        help_text=_('Book availability'),
    )
    # Chi dinh cac ban ghi se duoc sap xep theo truong 'due_back'
    class Meta:
        ordering = ['due_back']

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id} ({self.book.title})'

class Author(models.Model):
    """Model representing an author."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    # Chi dinh cac ban ghi se duoc sap xep theo truong 'last_name' va 'first_name'
    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """Returns the URL to access a particular author instance."""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.last_name}, {self.first_name}'
    