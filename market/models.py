from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

NIGERIAN_STATES=['Abia','Adamawa','Akwa Ibom','Anambra','Bauchi','Bayelsa','Benue','Borno','Cross River','Delta','Ebonyi','Edo','Ekiti','Enugu','Gombe','Imo','Jigawa','Kaduna','Kano','Katsina','Kebbi','Kogi','Kwara','Lagos','Nasarawa','Niger','Ogun','Ondo','Osun','Oyo','Plateau','Rivers','Sokoto','Taraba','Yobe','Zamfara','Federal Capital Territory']
CATEGORIES=[('floor','Floor Tiles'),('wall','Wall Tiles'),('porcelain','Porcelain Tiles'),('ceramic','Ceramic Tiles'),('marble','Marble Look'),('mosaic','Mosaic'),('outdoor','Outdoor Tiles'),('bathroom','Bathroom Tiles'),('kitchen','Kitchen Tiles'),('paving','Paving Tiles')]
FINISHES=[('glossy','Glossy'),('matt','Matt'),('polished','Polished'),('satin','Satin'),('textured','Textured'),('anti-slip','Anti-slip')]
ROLES=[('buyer','Buyer'),('seller','Seller'),('both','Buyer & Seller')]

class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    role=models.CharField(max_length=12,choices=ROLES,default='buyer')
    phone=models.CharField(max_length=30,blank=True); whatsapp=models.CharField(max_length=30,blank=True)
    business_name=models.CharField(max_length=160,blank=True); state=models.CharField(max_length=80,blank=True); city=models.CharField(max_length=100,blank=True)
    bio=models.TextField(blank=True); avatar=models.ImageField(upload_to='avatars/',blank=True,null=True)
    verified=models.BooleanField(default=False); created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.business_name or self.user.get_full_name() or self.user.username

class Tile(models.Model):
    STATUS=[('published','Published'),('pending','Pending'),('soldout','Sold Out'),('draft','Draft')]
    seller=models.ForeignKey(User,on_delete=models.CASCADE,related_name='tiles')
    name=models.CharField(max_length=180); slug=models.SlugField(unique=True,blank=True)
    brand=models.CharField(max_length=120); category=models.CharField(max_length=30,choices=CATEGORIES)
    description=models.TextField(); size=models.CharField(max_length=80); color=models.CharField(max_length=80,blank=True)
    finish=models.CharField(max_length=30,choices=FINISHES,default='matt'); material=models.CharField(max_length=100,default='Porcelain')
    tiles_per_box=models.PositiveIntegerField(default=1); coverage_per_box=models.DecimalField(max_digits=7,decimal_places=2,default=1)
    stock_boxes=models.PositiveIntegerField(default=0); price_per_box=models.DecimalField(max_digits=12,decimal_places=2); price_per_sqm=models.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    min_order=models.PositiveIntegerField(default=1); state=models.CharField(max_length=80,choices=[(s,s) for s in NIGERIAN_STATES]); city=models.CharField(max_length=100); area=models.CharField(max_length=120,blank=True)
    phone=models.CharField(max_length=30,blank=True); whatsapp=models.CharField(max_length=30,blank=True); video_url=models.URLField(blank=True)
    featured=models.BooleanField(default=False); verified=models.BooleanField(default=False); status=models.CharField(max_length=20,choices=STATUS,default='published')
    views=models.PositiveIntegerField(default=0); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta: ordering=['-featured','-created_at']; indexes=[models.Index(fields=['brand','category']),models.Index(fields=['state','city']),models.Index(fields=['price_per_box'])]
    def save(self,*args,**kwargs):
        if not self.slug:
            base=slugify(self.name) or 'tile'; self.slug=base; n=2
            while Tile.objects.filter(slug=self.slug).exclude(pk=self.pk).exists(): self.slug=f'{base}-{n}'; n+=1
        super().save(*args,**kwargs)
    def get_absolute_url(self): return reverse('tile_detail',args=[self.slug])
    @property
    def primary_media(self): return self.media.filter(kind='image').first()
    @property
    def seller_name(self):
        return getattr(self.seller,'profile',None) and (self.seller.profile.business_name or self.seller.get_full_name() or self.seller.username) or self.seller.username

class TileMedia(models.Model):
    KIND=[('image','Image'),('video','Video')]
    tile=models.ForeignKey(Tile,on_delete=models.CASCADE,related_name='media'); kind=models.CharField(max_length=10,choices=KIND,default='image')
    image=models.ImageField(upload_to='tiles/images/%Y/%m/',blank=True,null=True); video=models.FileField(upload_to='tiles/videos/%Y/%m/',blank=True,null=True)
    external_url=models.URLField(blank=True); caption=models.CharField(max_length=160,blank=True); created_at=models.DateTimeField(auto_now_add=True)

class Favorite(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='tile_favorites'); tile=models.ForeignKey(Tile,on_delete=models.CASCADE,related_name='favorites'); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: constraints=[models.UniqueConstraint(fields=['user','tile'],name='unique_tile_favorite')]

class TileLike(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE); tile=models.ForeignKey(Tile,on_delete=models.CASCADE,related_name='likes'); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: constraints=[models.UniqueConstraint(fields=['user','tile'],name='unique_tile_like')]

class Comment(models.Model):
    tile=models.ForeignKey(Tile,on_delete=models.CASCADE,related_name='comments'); user=models.ForeignKey(User,on_delete=models.CASCADE); body=models.TextField(); created_at=models.DateTimeField(auto_now_add=True); approved=models.BooleanField(default=True)

class Question(models.Model):
    tile=models.ForeignKey(Tile,on_delete=models.CASCADE,related_name='questions'); asker=models.ForeignKey(User,on_delete=models.CASCADE,related_name='questions_asked'); body=models.TextField(); answer=models.TextField(blank=True); answered_at=models.DateTimeField(null=True,blank=True); created_at=models.DateTimeField(auto_now_add=True)

class Conversation(models.Model):
    tile=models.ForeignKey(Tile,on_delete=models.CASCADE,related_name='conversations'); participants=models.ManyToManyField(User,related_name='tile_conversations'); updated_at=models.DateTimeField(auto_now=True); created_at=models.DateTimeField(auto_now_add=True)

class ChatMessage(models.Model):
    conversation=models.ForeignKey(Conversation,on_delete=models.CASCADE,related_name='messages'); sender=models.ForeignKey(User,on_delete=models.CASCADE); body=models.TextField(); read=models.BooleanField(default=False); created_at=models.DateTimeField(auto_now_add=True)

class Inquiry(models.Model):
    tile=models.ForeignKey(Tile,on_delete=models.CASCADE,related_name='inquiries'); buyer=models.ForeignKey(User,on_delete=models.CASCADE); quantity=models.PositiveIntegerField(default=1); message=models.TextField(); status=models.CharField(max_length=20,default='new',choices=[('new','New'),('contacted','Contacted'),('closed','Closed')]); created_at=models.DateTimeField(auto_now_add=True)

class Ad(models.Model):
    title=models.CharField(max_length=160); image=models.ImageField(upload_to='ads/',blank=True,null=True); target_url=models.URLField(blank=True); active=models.BooleanField(default=True); priority=models.PositiveIntegerField(default=0); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['-priority','-created_at']

class Notification(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='tile_notifications'); title=models.CharField(max_length=160); body=models.TextField(); url=models.CharField(max_length=255,blank=True); read=models.BooleanField(default=False); created_at=models.DateTimeField(auto_now_add=True)

class SavedSearch(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='saved_searches'); name=models.CharField(max_length=100); query=models.JSONField(default=dict); created_at=models.DateTimeField(auto_now_add=True)
