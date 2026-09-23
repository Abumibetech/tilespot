from .models import Ad

def site_context(request):
    ads=list(Ad.objects.filter(active=True)[:6])
    unread=0
    if request.user.is_authenticated:
        unread=request.user.tile_notifications.filter(read=False).count()
    return {'site_ads':ads,'unread_notifications':unread,'site_name':'Tilespot','site_tagline':'Nigeria’s modern marketplace for tiles.'}
