from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
from django.utils.html import strip_tags
from .models import UserProfile, User, Author, Publisher, LendPeriods, Book
from .validators import email_vailidator
from django.utils import timezone
from django.forms import ModelForm


class UserEditForm(forms.Form):
    """
    Form for editing User instances
    """
    username = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={'placeholder': 'Username'}))
    email = forms.EmailField(validators=[email_vailidator], required=False, widget=forms.widgets.EmailInput(attrs={'placeholder': 'Email'}))
    first_name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={'placeholder': 'Last Name'}))

    mobile = forms.CharField(required=False, widget=forms.widgets.TextInput(attrs={'placeholder': 'Mobile No.'}))
    website = forms.CharField(required=False, widget=forms.widgets.URLInput(attrs={'placeholder': 'Website address'}))

    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['readonly'] = True

    class Meta:
        fields = ['username', 'email', 'first_name', 'last_name', 'mobile', 'website']

    def is_valid(self):

        valid = super(UserEditForm, self).is_valid()
        # we're done now if not valid
        if not valid:
            return valid 

        for f, error in self.errors.iteritems():
            if f != '__all_':
                self.fields[f].widget.attrs.update({'class': 'error', 'value': strip_tags(error)})
        return self

    def clean_email(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')

        if email and User.objects.filter(email=email).exclude(username=username).count():
            e = forms.ValidationError(
                'This email address is already in use. Please supply a different email address.')
            raise e
        return email

    def save(self, user):
        user.email = self.cleaned_data.get('email')

        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.profile.mobile = self.cleaned_data.get('mobile')
        user.profile.website = self.cleaned_data.get('website')
        user.profile.save()
        user.save()
        return user


class UserCreateForm(UserCreationForm):
    """
    Form for creation user instances
    """
    username = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={'placeholder': 'Username'}))
    first_name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={'placeholder': 'Last Name'}))
    password1 = forms.CharField(required=True, widget=forms.widgets.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(required=True,
                                widget=forms.widgets.PasswordInput(attrs={'placeholder': 'Password Confirmation'}))

    def is_valid(self):
        form = super(UserCreateForm, self).is_valid()
        for f, error in self.errors.iteritems():
            if f != '__all_':
                self.fields[f].widget.attrs.update({'class': 'error', 'value': strip_tags(error)})
        return form

    def save(self):
        user = super(UserCreateForm, self).save()
        user_profile = UserProfile(user=user, join_date=timezone.now())
        user_profile.save()
        return user_profile

    class Meta:
        fields = ['username', 'first_name', 'last_name', 'password1',
                  'password2']
        model = User


class AuthenticateForm(AuthenticationForm):
    """
    Form to authenticate user
    """
    username = forms.CharField(widget=forms.widgets.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.widgets.PasswordInput(attrs={'placeholder': 'Password'}))

    def is_valid(self):
        form = super(AuthenticateForm, self).is_valid()
        for f, error in self.errors.iteritems():
            if f != '__all__':
                self.fields[f].widget.attrs.update({'class': 'error', 'value': strip_tags(error)})
        return form


class AuthorForm(ModelForm):
    """
    ModelForm to create and edit Author.
    """
    class Meta:
        model = Author
        fields = ['name', 'surname', 'date_of_birth', 'id']
        widgets = {
            'name': forms.widgets.TextInput(attrs={'placeholder': 'Name'}),
            'surname': forms.widgets.TextInput(attrs={'placeholder': 'Surname'}),
            'date_of_birth': forms.widgets.DateInput(attrs={'placeholder': 'Date of birth'}),
            'id': forms.widgets.HiddenInput(),
        }


class PublisherForm(ModelForm):
    """
    ModelForm to create and edit Publisher.
    """
    class Meta:
        model = Publisher
        fields = ['name']
        widgets = {
            'name': forms.widgets.TextInput(attrs={'placeholder': 'Name'}),
            }


class LendPeriodForm(ModelForm):
    """
    ModelForm to create and edit LendPeriod.
    """
    class Meta:
        model = LendPeriods
        fields = ['name', 'days_amount']
        widgets = {
            'name': forms.widgets.TextInput(attrs={'placeholder': 'Name'}),
            'days_amount': forms.widgets.TextInput(attrs={'placeholder': 'Amount of days'}),
            }


class BookForm(ModelForm):
    """
    ModelForm to create and edit Book.
    """
    class Meta:
        model = Book
        fields = ['title', 'ISBN', 'publisher', 'author', 'lend_period', 'page_amount']
        widgets = {
            'title': forms.widgets.TextInput(attrs={'placeholder': 'Title'}),
            'ISBN': forms.widgets.TextInput(attrs={'placeholder': 'ISBN'}),
            'publisher': forms.widgets.Select(),
            'author': forms.widgets.Select(attrs={'placeholder': 'Author'}),
            'lend_period': forms.widgets.Select(attrs={'placeholder': 'Lend period'}),
            'page_amount': forms.widgets.NumberInput(attrs={'min': 0, 'placeholder': 'Amount of pages'}),
            }
