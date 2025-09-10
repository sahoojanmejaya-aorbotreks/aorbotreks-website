from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from django.core.exceptions import ValidationError
import bleach
import uuid
import mimetypes
from .supabase_client import supabase
from ckeditor.fields import RichTextField
from io import BytesIO
from PIL import Image, ImageEnhance
from django.utils.html import mark_safe
import io

class Visitor(models.Model):
    ip_address = models.GenericIPAddressField()
    session_id = models.CharField(max_length=255, blank=True, db_index=True)
    user_agent = models.CharField(max_length=255, blank=True)
    visit_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["visit_time"]),
            models.Index(fields=["ip_address"]),
        ]

    def __str__(self):
        return f"{self.ip_address} @ {self.visit_time}"

def validate_image_file_extension(value):
    import os
    from django.template.defaultfilters import filesizeformat
    from django.conf import settings

    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. Allowed extensions are: ' + ', '.join(valid_extensions))

    # For a more secure approach, use python-magic to check the actual MIME type
    import magic
    try:
        mime_type = magic.from_buffer(value.read(1024), mime=True)
        value.seek(0) # Reset file pointer after reading
    except Exception as e:
        raise ValidationError(f"Could not determine file type: {e}")

    allowed_mime_types = ['image/jpeg', 'image/png', 'image/gif', 'image/svg+xml', 'image/webp']
    if mime_type not in allowed_mime_types:
        raise ValidationError(f'Unsupported file type. Detected: {mime_type}. Allowed types are: ' + ', '.join(allowed_mime_types))

    # Max file size check (example, adjust as needed)
    max_size = 5 * 1024 * 1024  # 5 MB
    if value.size > max_size:
        raise ValidationError(f'File size too large. Max size is {filesizeformat(max_size)}.')



# Create your models here.
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    mobile = models.CharField(max_length=20)
    user_type = models.CharField(max_length=50, blank=True, null=True)
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.name} - {self.email}"
    


class Blog(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = RichTextField()
    excerpt = models.TextField(max_length=300, blank=True, help_text="Short description for blog listings")
    image = models.ImageField(upload_to='blogs/', validators=[validate_image_file_extension], blank=True, null=True)
    original_image = models.ImageField(upload_to='blogs/originals/', validators=[validate_image_file_extension], blank=True, null=True)
    image_url = models.URLField(blank=True, null=True, editable=False)
    original_image_url = models.URLField(blank=True, null=True, editable=False)
    author = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def add_watermark(self, image_file):
        """Add centered watermark with low transparency"""
        image = Image.open(image_file).convert("RGBA")
        watermark = Image.open("static/images/background.png").convert("RGBA")  # your watermark logo

        # Resize watermark to 10% of image width
        w_ratio = int(image.width * 0.10)
        watermark = watermark.resize((w_ratio, int(watermark.height * (w_ratio / watermark.width))))

        # Reduce watermark transparency (light transparency)
        alpha = watermark.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(0.80)
        watermark.putalpha(alpha)

        # Position watermark
        x = (image.width - watermark.width) // 2
        y = (image.height - watermark.height) // 2
        image.paste(watermark, (x, y), watermark)

        # Save as WebP in memory
        output = BytesIO()
        image.convert("RGB").save(output, format="WEBP")
        output.seek(0)
        return output

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        bucket, folder = supabase.storage.from_("blogs"), "blogs"

        if self.image:
            if not self.original_image:
                original_file_name = f"{uuid.uuid4()}.webp"
                original_path = f"{folder}/originals/{original_file_name}"
                
                self.image.seek(0)
                file_content = BytesIO(self.image.read())
                
                bucket.upload(original_path, file_content.getvalue(), {"content-type": "image/webp"})
                self.original_image.name = original_path
                self.original_image_url = bucket.get_public_url(original_path)

            # Apply watermark
            self.image.seek(0)
            watermarked_image = self.add_watermark(self.image)
            file_name = f"{uuid.uuid4()}.webp"
            path = f"{folder}/{file_name}"
            bucket.upload(path, watermarked_image.read(), {"content-type": "image/webp"})
            self.image_url = bucket.get_public_url(path)
            self.image.name = file_name  

        else:
            # Remove images if cleared
            base_url = bucket.get_public_url("").rstrip("/") + "/"
            if self.image_url:
                file_path = self.image_url.replace(base_url, "", 1)
                bucket.remove([file_path])
            if self.original_image_url:
                original_path = self.original_image_url.replace(base_url, "", 1)
                bucket.remove([original_path])
            self.image = None
            self.original_image = None
            self.image_url = None
            self.original_image_url = None

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title


class TrekCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Trek Categories"
    
    def __str__(self):
        return self.name

class TrekOrganizer(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    logo = models.ImageField(upload_to='organizers/', validators=[validate_image_file_extension])
    website = models.URLField(blank=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class Trek(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('moderate', 'Moderate'),
        ('difficult', 'Difficult'),
        ('extreme', 'Extreme'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    short_description = models.TextField(max_length=300, blank=True)
    image = models.ImageField(upload_to='treks/', validators=[validate_image_file_extension])
    additional_images = models.ManyToManyField('TrekImage', blank=True, related_name='trek_images')
    category = models.ForeignKey(TrekCategory, on_delete=models.CASCADE, related_name='treks')
    organizer = models.ForeignKey(TrekOrganizer, on_delete=models.CASCADE, related_name='treks')
    duration = models.CharField(max_length=50, help_text="e.g., '2 days, 1 night'")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    location = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('trek_detail', kwargs={'slug': self.slug})

class TrekImage(models.Model):
    image = models.ImageField(upload_to='trek_images/', validators=[validate_image_file_extension])
    caption = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return self.caption or f"Image {self.id}"

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='testimonials/', blank=True, null=True, validators=[validate_image_file_extension])
    trek = models.ForeignKey(Trek, on_delete=models.SET_NULL, null=True, blank=True, related_name='testimonials')
    trek_name = models.CharField(max_length=200, blank=True, help_text="Only required if trek is not selected")
    date = models.DateField()
    content = models.TextField()
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    is_featured = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        # Sanitize content before saving to prevent XSS
        self.content = bleach.clean(self.content, tags=[], attributes={}, strip=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.trek or self.trek_name}"

class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('booking', 'Booking & Payment'),
        ('treks', 'Treks & Activities'),
        ('safety', 'Safety & Equipment'),
        ('Cancellation & Refund', 'Cancellation & Refund'),
        ('Payment-Related', 'Payment-Related'),
        ('Customer-support', 'Customer-Support'),
    ]
    
    question = models.CharField(max_length=300)
    answer = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    order = models.PositiveIntegerField(default=0, help_text="Order of display")
    
    class Meta:
        ordering = ['category', 'order']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
    
    def __str__(self):
        return self.question

class SafetyTip(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    icon = models.ImageField(upload_to='safety_icons/', blank=True, null=True, validators=[validate_image_file_extension])
    order = models.PositiveIntegerField(default=0, help_text="Order of display")
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title

class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    bio = models.TextField()
    photo = models.ImageField(upload_to='team/', validators=[validate_image_file_extension])
    email = models.EmailField(blank=True)
    linkedin = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Order of display")
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.name} - {self.position}"

class HomepageBanner(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='banners/', validators=[validate_image_file_extension])
    button_text = models.CharField(max_length=50, blank=True)
    button_url = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Order of display")
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title

class SocialMedia(models.Model):
    platform = models.CharField(max_length=50)
    url = models.URLField()
    icon = models.ImageField(upload_to='social_icons/', blank=True, null=True, validators=[validate_image_file_extension])
    order = models.PositiveIntegerField(default=0, help_text="Order of display")
    
    class Meta:
        ordering = ['order']
        verbose_name_plural = "Social Media Links"
    
    def __str__(self):
        return self.platform

class ContactInfo(models.Model):
    company_name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    map_url = models.URLField(blank=True, help_text="Google Maps URL")
    
    class Meta:
        verbose_name_plural = "Contact Information"
    
    def __str__(self):
        return self.company_name

# class WhatsNew(models.Model):
#     title = models.CharField(max_length=200)
#     content = models.TextField()
#     image = models.ImageField(upload_to="whatsnew/", blank=True, null=True)
#     image_url = models.URLField(blank=True, null=True, editable=False)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def save(self, *args, **kwargs):
#         bucket, folder = supabase.storage.from_("blogs"), "whatsnew"
#         if self.image:
#             ext = self.image.name.split('.')[-1]
#             file_name = f"{uuid.uuid4()}.{ext}"
#             path = f"{folder}/{file_name}"
#             mime, _ = mimetypes.guess_type(self.image.name)
#             if not mime:
#                 mime = "application/octet-stream"
#             bucket.upload(path, self.image.read(), {"content-type": mime})
#             self.image_url = bucket.get_public_url(path)
#             self.image.name = file_name  
#         elif not self.image and self.image_url:
#             base_url = bucket.get_public_url("").rstrip("/") + "/"
#             file_path = self.image_url.replace(base_url, "", 1)
#             bucket.remove([file_path])
#             self.image = None
#             self.image_url = None
#         super().save(*args, **kwargs)
#     def _str_(self):
#         return self.title



# class TopTrek(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.TextField()
#     image = models.ImageField(upload_to="toptreks/", blank=True, null=True)
#     image_url = models.URLField(blank=True, null=True, editable=False)

#     def save(self, *args, **kwargs):
#         bucket, folder = supabase.storage.from_("blogs"), "toptreks"
#         if self.image:
#             ext = self.image.name.split('.')[-1]
#             file_name = f"{uuid.uuid4()}.{ext}"
#             path = f"{folder}/{file_name}"
#             mime, _ = mimetypes.guess_type(self.image.name)
#             if not mime:
#                 mime = "application/octet-stream"
#             bucket.upload(path, self.image.read(), {"content-type": mime})
#             self.image_url = bucket.get_public_url(path)
#         elif not self.image and self.image_url:
#             base = bucket.get_public_url("").rstrip("/") + "/"
#             bucket.remove([self.image_url.replace(base, "", 1)])
#             self.image = None
#             self.image_url = None

#         super().save(*args, **kwargs)

#     def _str_(self):
#         return self.name

class WhatsNew(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to="whatsnew/", blank=True, null=True)
    image_url = models.URLField(blank=True, null=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        bucket, folder = supabase.storage.from_("blogs"), "whatsnew"

        if self.image:
            ext = self.image.name.split('.')[-1].lower()
            file_name = f"{uuid.uuid4()}.{ext}"
            path = f"{folder}/{file_name}"

            # Compress image before upload
            img = Image.open(self.image)
            img_io = io.BytesIO()
            if ext in ["jpg", "jpeg"]:
                img.save(img_io, format="JPEG", optimize=True, quality=70)  # adjust quality
            elif ext == "png":
                img.save(img_io, format="PNG", optimize=True)
            else:
                img.save(img_io, format=img.format)

            img_io.seek(0)

            mime, _ = mimetypes.guess_type(self.image.name)
            if not mime:
                mime = "application/octet-stream"

            bucket.upload(path, img_io.getvalue(), {"content-type": mime})
            self.image_url = bucket.get_public_url(path)
            self.image.name = file_name  

        elif not self.image and self.image_url:
            base_url = bucket.get_public_url("").rstrip("/") + "/"
            file_path = self.image_url.replace(base_url, "", 1)
            bucket.remove([file_path])
            self.image = None
            self.image_url = None

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class TopTrek(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="toptreks/", blank=True, null=True)
    image_url = models.URLField(blank=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        bucket, folder = supabase.storage.from_("blogs"), "toptreks"

        if self.image:
            ext = self.image.name.split('.')[-1].lower()
            file_name = f"{uuid.uuid4()}.{ext}"
            path = f"{folder}/{file_name}"

            # Compress image before upload
            img = Image.open(self.image)
            img_io = io.BytesIO()
            if ext in ["jpg", "jpeg"]:
                img.save(img_io, format="JPEG", optimize=True, quality=70)
            elif ext == "png":
                img.save(img_io, format="PNG", optimize=True)
            else:
                img.save(img_io, format=img.format)

            img_io.seek(0)

            mime, _ = mimetypes.guess_type(self.image.name)
            if not mime:
                mime = "application/octet-stream"

            bucket.upload(path, img_io.getvalue(), {"content-type": mime})
            self.image_url = bucket.get_public_url(path)
            self.image.name = file_name  

        elif not self.image and self.image_url:
            base = bucket.get_public_url("").rstrip("/") + "/"
            bucket.remove([self.image_url.replace(base, "", 1)])
            self.image = None
            self.image_url = None

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    


class TermsAndConditions(models.Model):
    title = models.CharField(max_length=255, default="Terms and Conditions")
    content = RichTextField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} (Last updated: {self.updated_at.strftime('%Y-%m-%d')})"

    def content_preview(self):
        return mark_safe(self.content[:300] + "...")