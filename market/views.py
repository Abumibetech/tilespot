from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import *
from .forms import *


def profile_for(user):
    return Profile.objects.get_or_create(user=user)[0]


def seller_allowed(user):
    return profile_for(user).role in ('seller', 'both')


def home(request):
    featured = (
        Tile.objects
        .filter(status='published')
        .prefetch_related('media', 'likes', 'favorites')
        .order_by('-featured', '-created_at')[:8]
    )

    latest = (
        Tile.objects
        .filter(status='published')
        .prefetch_related('media')
        .order_by('-created_at')[:8]
    )

    popular = (
        Tile.objects
        .filter(status='published')
        .values('brand')
        .annotate(total=Count('id'))
        .order_by('-total')[:8]
    )

    return render(
        request,
        'market/home.html',
        {
            'featured': featured,
            'latest': latest,
            'popular_brands': popular,
            'states': NIGERIAN_STATES,
            'categories': CATEGORIES,
        }
    )


def catalog(request):
    qs = (
        Tile.objects
        .filter(status='published')
        .select_related('seller', 'seller__profile')
        .prefetch_related('media')
    )

    params = {
        k: request.GET.get(k, '').strip()
        for k in [
            'q',
            'brand',
            'category',
            'state',
            'city',
            'size',
            'finish',
            'color',
            'sort'
        ]
    }

    if params['q']:
        qs = qs.filter(
            Q(name__icontains=params['q']) |
            Q(brand__icontains=params['q']) |
            Q(description__icontains=params['q']) |
            Q(city__icontains=params['q']) |
            Q(area__icontains=params['q']) |
            Q(size__icontains=params['q']) |
            Q(color__icontains=params['q'])
        )

    for k in ['brand', 'category', 'state', 'city', 'size', 'finish', 'color']:
        if params[k]:
            qs = qs.filter(**{k + '__icontains': params[k]})

    if request.GET.get('min_price', '').isdigit():
        qs = qs.filter(
            price_per_box__gte=request.GET['min_price']
        )

    if request.GET.get('max_price', '').isdigit():
        qs = qs.filter(
            price_per_box__lte=request.GET['max_price']
        )

    if params['sort'] == 'price_low':
        qs = qs.order_by('price_per_box')

    elif params['sort'] == 'price_high':
        qs = qs.order_by('-price_per_box')

    elif params['sort'] == 'popular':
        qs = qs.order_by('-views')

    elif params['sort'] == 'newest':
        qs = qs.order_by('-created_at')

    else:
        qs = qs.order_by('-featured', '-created_at')

    return render(
        request,
        'market/catalog.html',
        {
            'tiles': qs,
            'states': NIGERIAN_STATES,
            'categories': CATEGORIES,
            'brands': (
                Tile.objects
                .filter(status='published')
                .values_list('brand', flat=True)
                .distinct()
                .order_by('brand')
            ),
            'params': params,
            'result_count': qs.count(),
        }
    )


def tile_detail(request, slug):
    tile = get_object_or_404(
        Tile.objects
        .select_related('seller', 'seller__profile')
        .prefetch_related(
            'media',
            'comments__user',
            'questions__asker'
        ),
        slug=slug,
        status='published'
    )

    Tile.objects.filter(pk=tile.pk).update(
        views=tile.views + 1
    )

    liked = (
        request.user.is_authenticated
        and tile.likes.filter(user=request.user).exists()
    )

    favorite = (
        request.user.is_authenticated
        and tile.favorites.filter(user=request.user).exists()
    )

    related = (
        Tile.objects
        .filter(
            status='published',
            category=tile.category
        )
        .exclude(pk=tile.pk)[:4]
    )

    return render(
        request,
        'market/detail.html',
        {
            'tile': tile,
            'liked': liked,
            'favorite': favorite,
            'comment_form': CommentForm(),
            'question_form': QuestionForm(),
            'inquiry_form': InquiryForm(),
            'related': related,
        }
    )


def register(request):
    f = RegisterForm(request.POST or None)

    if request.method == 'POST' and f.is_valid():
        u = f.save()

        p = profile_for(u)
        p.role = f.cleaned_data['role']
        p.phone = f.cleaned_data['phone']
        p.save()

        login(request, u)

        messages.success(
            request,
            f'Welcome to Tilespot, {u.first_name or u.username}. Your {p.get_role_display()} account is ready.'
        )

        return redirect('dashboard')

    return render(
        request,
        'registration/register.html',
        {'form': f}
    )


def login_view(request):
    if request.method == 'POST':
        u = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )

        if u:
            login(request, u)

            return redirect(
                request.GET.get('next') or 'dashboard'
            )

        messages.error(
            request,
            'Invalid username or password.'
        )

    return render(
        request,
        'registration/login.html'
    )


def logout_view(request):
    logout(request)

    messages.success(
        request,
        'You have been logged out successfully.'
    )

    return redirect('home')


@login_required
def create_tile(request):
    profile_obj = profile_for(request.user)

    if profile_obj.role not in ('seller', 'both'):
        messages.error(
            request,
            'A Buyer account cannot create tile listings. Switch your account to Buyer & Seller from your profile if you want to sell.'
        )
        return redirect('dashboard')

    f = TileForm(request.POST or None)

    if request.method == 'POST' and f.is_valid():
        t = f.save(commit=False)
        t.seller = request.user
        t.status = 'published'
        t.save()

        messages.success(
            request,
            'Your tile listing has been created. Add photos and videos next.'
        )

        return redirect(
            'tile_media',
            t.pk
        )

    return render(
        request,
        'market/tile_form.html',
        {
            'form': f,
            'title': 'List tiles for sale'
        }
    )


@login_required
def edit_tile(request, pk):
    profile_obj = profile_for(request.user)

    if profile_obj.role not in ('seller', 'both'):
        messages.error(
            request,
            'Only sellers can edit tile listings.'
        )
        return redirect('dashboard')

    t = get_object_or_404(
        Tile,
        pk=pk,
        seller=request.user
    )

    f = TileForm(
        request.POST or None,
        instance=t
    )

    if request.method == 'POST' and f.is_valid():
        f.save()

        messages.success(
            request,
            'Listing updated.'
        )

        return redirect(
            'tile_detail',
            t.slug
        )

    return render(
        request,
        'market/tile_form.html',
        {
            'form': f,
            'title': 'Edit tile listing',
            'tile': t
        }
    )


@login_required
def tile_media(request, pk):
    profile_obj = profile_for(request.user)

    if profile_obj.role not in ('seller', 'both'):
        messages.error(
            request,
            'Only sellers can upload listing media.'
        )
        return redirect('dashboard')

    t = get_object_or_404(
        Tile,
        pk=pk,
        seller=request.user
    )

    f = MediaForm(
        request.POST or None,
        request.FILES or None
    )

    if request.method == 'POST' and f.is_valid():
        images = f.cleaned_data.get('images') or []
        videos = f.cleaned_data.get('videos') or []

        if not images and not videos:
            messages.error(
                request,
                'Select at least one image or video.'
            )

            return render(
                request,
                'market/media.html',
                {
                    'tile': t,
                    'form': f
                }
            )

        for x in images:
            TileMedia.objects.create(
                tile=t,
                kind='image',
                image=x
            )

        for x in videos:
            TileMedia.objects.create(
                tile=t,
                kind='video',
                video=x
            )

        messages.success(
            request,
            f'{len(images)} image(s) and {len(videos)} video(s) uploaded successfully.'
        )

        return redirect(
            'tile_detail',
            t.slug
        )

    return render(
        request,
        'market/media.html',
        {
            'tile': t,
            'form': f
        }
    )


@login_required
def like_tile(request, pk):
    t = get_object_or_404(
        Tile,
        pk=pk
    )

    obj, created = TileLike.objects.get_or_create(
        user=request.user,
        tile=t
    )

    if not created:
        obj.delete()

    return redirect(
        request.META.get('HTTP_REFERER')
        or t.get_absolute_url()
    )


@login_required
def favorite_tile(request, pk):
    t = get_object_or_404(
        Tile,
        pk=pk
    )

    obj, created = Favorite.objects.get_or_create(
        user=request.user,
        tile=t
    )

    if not created:
        obj.delete()

    return redirect(
        request.META.get('HTTP_REFERER')
        or t.get_absolute_url()
    )


@login_required
def comment_tile(request, pk):
    t = get_object_or_404(
        Tile,
        pk=pk
    )

    f = CommentForm(request.POST)

    if f.is_valid():
        x = f.save(commit=False)
        x.tile = t
        x.user = request.user
        x.save()

        messages.success(
            request,
            'Comment posted.'
        )

    return redirect(
        t.get_absolute_url()
    )


@login_required
def question_tile(request, pk):
    t = get_object_or_404(
        Tile,
        pk=pk
    )

    f = QuestionForm(request.POST)

    if f.is_valid():
        x = f.save(commit=False)
        x.tile = t
        x.asker = request.user
        x.save()

        Notification.objects.create(
            user=t.seller,
            title='New buyer question',
            body=f'{request.user.username} asked about {t.name}',
            url=t.get_absolute_url()
        )

        messages.success(
            request,
            'Question sent to the seller.'
        )

    return redirect(
        t.get_absolute_url()
    )


@login_required
def inquiry_tile(request, pk):
    t = get_object_or_404(
        Tile,
        pk=pk
    )

    f = InquiryForm(request.POST)

    if f.is_valid():
        x = f.save(commit=False)
        x.tile = t
        x.buyer = request.user
        x.save()

        Notification.objects.create(
            user=t.seller,
            title='New tile inquiry',
            body=f'{request.user.username} is interested in {t.name}',
            url=t.get_absolute_url()
        )

        messages.success(
            request,
            'Your enquiry has been sent to the seller.'
        )

    return redirect(
        t.get_absolute_url()
    )


@login_required
def dashboard(request):
    profile_obj = profile_for(request.user)

    my = (
        Tile.objects
        .filter(seller=request.user)
        .prefetch_related('media')
    )

    fav = (
        Favorite.objects
        .filter(user=request.user)
        .select_related('tile')
        .prefetch_related('tile__media')
    )

    if profile_obj.role in ('seller', 'both'):
        inquiries = (
            Inquiry.objects
            .filter(tile__seller=request.user)
            .select_related('tile', 'buyer')
            .order_by('-created_at')[:10]
        )
    else:
        inquiries = (
            Inquiry.objects
            .filter(buyer=request.user)
            .select_related('tile', 'tile__seller')
            .order_by('-created_at')[:10]
        )

    return render(
        request,
        'market/dashboard.html',
        {
            'my_tiles': my,
            'favorites': fav,
            'inquiries': inquiries,
            'profile': profile_obj,
            'is_seller': profile_obj.role in ('seller', 'both'),
            'is_buyer': profile_obj.role in ('buyer', 'both'),
        }
    )


@login_required
def profile(request):
    p = profile_for(request.user)

    f = ProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=p
    )

    if request.method == 'POST' and f.is_valid():
        f.save()

        messages.success(
            request,
            'Profile updated.'
        )

        return redirect('profile')

    return render(
        request,
        'market/profile.html',
        {'form': f}
    )


@login_required
def start_conversation(request, pk):
    t = get_object_or_404(
        Tile,
        pk=pk,
        status='published'
    )

    c = (
        Conversation.objects
        .filter(
            tile=t,
            participants=request.user
        )
        .filter(
            participants=t.seller
        )
        .first()
    )

    if not c:
        c = Conversation.objects.create(
            tile=t
        )

        c.participants.add(
            request.user,
            t.seller
        )

    return redirect(
        'conversation',
        c.pk
    )


@login_required
def inbox(request):
    return render(
        request,
        'market/messages.html',
        {
            'conversations': (
                request.user
                .tile_conversations
                .all()
                .order_by('-updated_at')
            )
        }
    )


@login_required
def conversation(request, pk):
    c = get_object_or_404(
        Conversation,
        pk=pk,
        participants=request.user
    )

    if request.method == 'POST' and request.POST.get('body'):
        ChatMessage.objects.create(
            conversation=c,
            sender=request.user,
            body=request.POST['body']
        )

        c.save()

        return redirect(
            'conversation',
            pk
        )

    c.messages.exclude(
        sender=request.user
    ).update(
        read=True
    )

    return render(
        request,
        'market/conversation.html',
        {
            'conversation': c
        }
    )


@login_required
def notifications(request):
    qs = (
        request.user
        .tile_notifications
        .order_by('-created_at')
    )

    qs.filter(
        read=False
    ).update(
        read=True
    )

    return render(
        request,
        'market/notifications.html',
        {
            'notifications': qs
        }
    )


@login_required
def save_search(request):
    SavedSearch.objects.create(
        user=request.user,
        name=request.POST.get(
            'name',
            'My tile search'
        ),
        query=dict(request.POST)
    )

    messages.success(
        request,
        'Search saved to your account.'
    )

    return redirect(
        request.META.get('HTTP_REFERER')
        or 'catalog'
    )


def robots(request):
    return HttpResponse(
        'User-agent: *\n'
        'Allow: /\n'
        'Sitemap: /sitemap.xml\n',
        content_type='text/plain'
    )