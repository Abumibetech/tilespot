from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile, Tile, TileMedia, Comment, Question, Inquiry


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=[('buyer', 'Buyer'), ('seller', 'Seller'), ('both', 'Buyer & Seller')],
        initial='buyer'
    )
    phone = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.email = self.cleaned_data['email']
            user.save(update_fields=['email'])
        return user


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_clean(item, initial) for item in data]
        return single_clean(data, initial)


class TileForm(forms.ModelForm):
    class Meta:
        model = Tile
        exclude = ('seller', 'slug', 'views', 'featured', 'verified', 'status')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'video_url': forms.URLInput(
                attrs={'placeholder': 'Optional YouTube, TikTok, Instagram or video URL'}
            ),
        }


class MediaForm(forms.Form):
    images = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={'multiple': True, 'accept': 'image/jpeg,image/png,image/webp'})
    )
    videos = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={'multiple': True, 'accept': 'video/mp4,video/webm,video/quicktime'})
    )

    def clean_images(self):
        files = self.cleaned_data.get('images') or []
        if not isinstance(files, (list, tuple)):
            files = [files]
        for f in files:
            if f and f.size > 10 * 1024 * 1024:
                raise forms.ValidationError(f'{f.name} is larger than the 10 MB image limit.')
            if f and not (f.content_type or '').startswith('image/'):
                raise forms.ValidationError(f'{f.name} is not a valid image.')
        return files

    def clean_videos(self):
        files = self.cleaned_data.get('videos') or []
        if not isinstance(files, (list, tuple)):
            files = [files]
        allowed = {'video/mp4', 'video/webm', 'video/quicktime'}
        for f in files:
            if f and f.size > 100 * 1024 * 1024:
                raise forms.ValidationError(f'{f.name} is larger than the 100 MB video limit.')
            if f and (f.content_type or '') not in allowed:
                raise forms.ValidationError(f'{f.name} is not a supported video format.')
        return files


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('role', 'phone', 'whatsapp', 'business_name', 'state', 'city', 'bio', 'avatar')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)
        widgets = {'body': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Share your thoughts about this tile...'})}


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('body',)
        widgets = {'body': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ask the seller a question...'})}


class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ('quantity', 'message')
        widgets = {'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell the seller what you need, delivery location, etc.'})}
