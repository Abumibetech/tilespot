from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from market.models import Profile,Tile,TileMedia,Ad

# Finished-space photographs. They show tiles/interiors in use rather than isolated house icons.
ROOMS=[
'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1400&q=88',
'https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?auto=format&fit=crop&w=1400&q=88',
'https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=1400&q=88',
'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1400&q=88',
'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1400&q=88',
'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=1400&q=88',
]
DATA=[
('RAK Marble Look Calacatta','RAK Ceramics','porcelain','60x120 cm','Polished','White/Gold','Lagos','Lekki',62000,70),
('VitrA Stone Grey','VitrA','porcelain','60x60 cm','Matt','Grey','Federal Capital Territory','Gwarinpa',28500,120),
('Porcelanosa Urban Sand','Porcelanosa','porcelain','60x60 cm','Matt','Sand','Rivers','Port Harcourt',39000,80),
('Kajaria Emerald Wall','Kajaria','wall','30x60 cm','Glossy','Emerald','Lagos','Ikeja',24500,95),
('Atlas Concorde Nero Marble','Atlas Concorde','marble','60x120 cm','Polished','Black','Oyo','Ibadan',72000,45),
('Somany Terrazzo Neutral','Somany','floor','60x60 cm','Satin','Ivory','Enugu','Enugu',26000,100),
('RAK Blue Mosaic','RAK Ceramics','mosaic','30x30 cm','Glossy','Blue','Akwa Ibom','Uyo',18500,90),
('VitrA Outdoor Grip','VitrA','outdoor','40x40 cm','Anti-slip','Charcoal','Kaduna','Kaduna',29500,130),
('Porcelanosa Calacatta Luxe','Porcelanosa','marble','60x120 cm','Polished','Cream/Gold','Ogun','Abeokuta',76000,45),
('Kajaria Modern Concrete','Kajaria','floor','60x60 cm','Matt','Concrete Grey','Kano','Kano',24000,110),
('Somany Pearl Bathroom','Somany','bathroom','30x60 cm','Glossy','Pearl','Delta','Asaba',21000,100),
('Atlas Concorde Warm Wood','Atlas Concorde','floor','20x120 cm','Matt','Walnut','Anambra','Awka',45000,75),
]
class Command(BaseCommand):
    help='Seed a realistic Nigerian Tilespot marketplace with real-world tile brand names and finished-room imagery.'
    def handle(self,*args,**kwargs):
        sellers=[]
        seed_sellers=[('lagostiles','Lagos Tile Gallery','Lagos','Ikeja'),('capitaltiles','Capital Surfaces Hub','Federal Capital Territory','Gwarinpa'),('easternsurfaces','Eastern Surfaces','Enugu','Enugu'),('porttiles','Rivers Tile Market','Rivers','Port Harcourt')]
        for username,business,state,city in seed_sellers:
            u,_=User.objects.get_or_create(username=username,defaults={'first_name':business.split()[0],'email':username+'@tilespot.local'}); u.set_password('Tilespot123!'); u.save()
            p,_=Profile.objects.get_or_create(user=u); p.role='seller'; p.business_name=business; p.city=city; p.state=state; p.phone='+234 800 000 0000'; p.whatsapp='+234 800 000 0000'; p.verified=False; p.save(); sellers.append(u)
        for i,row in enumerate(DATA):
            name,brand,cat,size,finish,color,state,city,price,stock=row; seller=sellers[i%len(sellers)]
            t,_=Tile.objects.get_or_create(name=name,brand=brand,city=city,defaults={'seller':seller,'category':cat,'description':f'{brand} {name} — marketplace listing for {size} {cat.replace("_"," ")} tiles. The showcase image is a finished-space reference so buyers can judge the style in a real room. Ask the seller to confirm current batch, shade, stock, delivery and exact product specification before purchase.','size':size,'finish':finish,'color':color,'material':'Porcelain' if cat in ['porcelain','marble'] else 'Ceramic','tiles_per_box':4,'coverage_per_box':1.44,'stock_boxes':stock,'price_per_box':price,'price_per_sqm':round(price/1.44,2),'min_order':1,'state':state,'area':city,'phone':seller.profile.phone,'whatsapp':seller.profile.whatsapp,'featured':i<6,'verified':False,'status':'published'})
            # keep seed repeatable while ensuring every demo listing has a finished-room image
            if not t.media.exists(): TileMedia.objects.create(tile=t,kind='image',external_url=ROOMS[i%len(ROOMS)],caption=f'{name} — finished room inspiration')
        for i,title in enumerate(['Tilespot: list your stock and reach buyers across Nigeria','Need tiles for a building project? Compare sizes, finishes and stock','Sellers: add WhatsApp and multiple room photos to your listings']): Ad.objects.get_or_create(title=title,defaults={'target_url':'/tiles/','priority':30-i})
        self.stdout.write(self.style.SUCCESS('Tilespot seed complete. Demo seller password: Tilespot123!'))
