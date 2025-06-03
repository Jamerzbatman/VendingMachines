from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path
from pages import views as page
from leads import views as leads
from dashBoardSettings import views as dSettings

urlpatterns = [
    path('admin/', admin.site.urls),

    path('login/', auth_views.LoginView.as_view(template_name='pages/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    path('', page.home, name='home'),
    path('Learn-More/', page.learnMore, name='learnMore'),
    path('Sell-To-Us/', page.sellToUs, name='sellToUs'),
    path('Privacy/', page.privacy, name='privacy'),
    path('Terms/', page.terms, name='terms'),
    path('Thank-you/', page.thankYou, name='thankYou'),
    path('Dashboard/', page.dashboard, name='dashboard'),
    path('Ai-Tools/', page.aiTools, name='aiTools'),
    path('Leads/', page.leads, name='leads'),
    path('Inventory/', page.inventory, name='inventory'),
    path('Reports/', page.reports, name='reports'),
    path('Settings/', page.settings, name='settings'),
    path('About-Us/', page.aboutUs, name='aboutUs'),

    path('submit-webSite-lead/', leads.submitWebSiteLead, name='submitWebSiteLead'),
    path('Generate-Leads/', leads.generate_leads, name='generate_leads'),
    path('leads/progress/<uuid:job_id>/', leads.lead_progress, name='lead-progress'),
    path('leads/results/<uuid:job_id>/', leads.lead_results, name='lead_results'),
    path('Leads/Details/<int:lead_id>/', leads.lead_detail, name='lead_detail'),

    path('Update-Lead-Settings/', dSettings.update_lead_settings, name='update_lead_settings'),
    path('Add-Api-Key/', dSettings.add_api_key, name='add_api_key'),
    path('Update-ApiKey-Settings/', dSettings.update_ApiKey_settings, name='update_ApiKey_settings'),
    path('Add-Keywords/', dSettings.add_keywords, name='add_keywords'),
    path('Get-Location/', dSettings.get_location, name='get_location'),
    path('Save-Updated-Points/', dSettings.save_updated_points, name='save_updated_points'),
    path('get-location-points/<int:location_id>/', dSettings.get_location_points, name='get_location_points'),
    path('save-updated-location/<int:location_id>/', dSettings.save_updated_location, name='save_updated_location'),
    path('delete-location/<int:location_id>/', dSettings.delete_location, name='delete_location'),

]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

