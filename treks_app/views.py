from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.core.paginator import Paginator
import json
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.shortcuts import render



@api_view(['POST'])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def contact_submit(request):
    try:
        # Get data from POST request
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')
            mobile = data.get('mobile')
            user_type = data.get('userType')
            comment = data.get('comment')
        else:
            # Handle form data
            name = request.POST.get('name')
            email = request.POST.get('email')
            mobile = request.POST.get('mobile')
            user_type = request.POST.get('userType')
            comment = request.POST.get('comment')
        
        # Validate required fields
        if not all([name, email, mobile, comment]):
            return JsonResponse({'error': 'All fields are required'}, status=400)
            
        # Create a new Contact object
        contact = Contact(
            name=name,
            email=email,
            mobile=mobile,
            user_type=user_type,
            comment=comment
        )
        contact.save()
        
        return JsonResponse({'message': 'Contact form submitted successfully'}, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
from .models import (
    Contact, Blog, TrekCategory, TrekOrganizer, Trek, 
    Testimonial, FAQ, SafetyTip, TeamMember, HomepageBanner,
    SocialMedia, ContactInfo,WhatsNew, TopTrek
)


# Create your views here.
def home(request):
    featured_treks = Trek.objects.filter(is_featured=True)[:6]
    featured_testimonials = Testimonial.objects.filter(is_featured=True)[:6]
    featured_blogs = Blog.objects.filter(is_featured=True)[:3]
    banners = HomepageBanner.objects.filter(is_active=True).order_by('order')
    faqs = FAQ.objects.all().order_by('category', 'order')
    whats_new = WhatsNew.objects.all().order_by('-created_at')[:5]
    top_treks = TopTrek.objects.all()[:6]

    
    faq_categories = {}
    for faq in faqs:
        if faq.category not in faq_categories:
            faq_categories[faq.category] = []
        faq_categories[faq.category].append(faq)
    
    context = {
        'featured_treks': featured_treks,
        'featured_testimonials': featured_testimonials,
        'featured_blogs': featured_blogs,
        'banners': banners,
        'faq_categories': faq_categories,
        'whats_new': whats_new,
        'top_treks': top_treks,
    }
    return render(request, 'index.html', context)

# def home(request):
#     whats_new = WhatsNew.objects.all().order_by('-created_at')[:5]
#     top_treks = TopTrek.objects.all()[:]

#     context = {
#         'whats_new': whats_new,
#         'top_treks': top_treks,
#     }
#     return render(request, 'test.html', context)


def about(request):
    team_members = TeamMember.objects.all().order_by('order')
    context = {
        'team_members': team_members,
    }
    return render(request, 'about.html', context)

def blogs(request):
    all_blogs = Blog.objects.all().order_by('-created_at')[:6]
    paginator = Paginator(all_blogs, 6)  # Show 6 blogs per page
    
    page_number = request.GET.get('page')
    blogs = paginator.get_page(page_number)
    
    context = {
        'blogs': blogs,
    }
    return render(request, 'blogs.html', context)

def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    recent_blogs = Blog.objects.exclude(id=blog.id).order_by('-created_at')[:3]
    
    context = {
        'blog': blog,
        'recent_blogs': recent_blogs,
    }
    return render(request, 'blog_detail.html', context)

def treks(request):
    category_id = request.GET.get('category')
    difficulty = request.GET.get('difficulty')
    
    all_treks = Trek.objects.all()
    
    # Apply filters if provided
    if category_id:
        all_treks = all_treks.filter(category_id=category_id)
    if difficulty:
        all_treks = all_treks.filter(difficulty=difficulty)
    
    # Get all categories for filter dropdown
    categories = TrekCategory.objects.all()
    
    paginator = Paginator(all_treks, 12)  # Show 12 treks per page
    page_number = request.GET.get('page')
    treks = paginator.get_page(page_number)
    
    context = {
        'treks': treks,
        'categories': categories,
        'selected_category': category_id,
        'selected_difficulty': difficulty,
        'difficulty_choices': Trek.DIFFICULTY_CHOICES,
    }
    return render(request, 'treks.html', context)

def trek_detail(request, slug):
    trek = get_object_or_404(Trek, slug=slug)
    testimonials = trek.testimonials.all()
    similar_treks = Trek.objects.filter(category=trek.category).exclude(id=trek.id)[:3]
    
    context = {
        'trek': trek,
        'testimonials': testimonials,
        'similar_treks': similar_treks,
    }
    return render(request, 'trek_detail.html', context)

def safety(request):
    safety_tips = SafetyTip.objects.all().order_by('order')
    context = {
        'safety_tips': safety_tips,
    }
    return render(request, 'safety.html', context)

def contact(request):
    try:
        contact_info = ContactInfo.objects.first()
    except ContactInfo.DoesNotExist:
        contact_info = None
        
    social_media = SocialMedia.objects.all().order_by('order')
    
    context = {
        'contact_info': contact_info,
        'social_media': social_media,
    }
    return render(request, 'contact.html', context)

def privacy_policy(request):
    return render(request, 'privacypolicy.html')
def terms_and_conditions(request):
    return render(request, 'terms_and_conditions.html')
def user_agreement(request):
    return render(request, 'user_agreement.html')

def index(request):
    whats_new = WhatsNew.objects.all().order_by('-date_posted')[:3]
    top_treks = TopTrek.objects.all()[:4]
    return render(request, 'index.html', {
        'whats_new': whats_new,
        'top_treks': top_treks,
    })

