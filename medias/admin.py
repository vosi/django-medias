import re
import urlparse
from django.conf import settings
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _
from django.template.defaultfilters import filesizeformat, escapejs
from medias.models import File


class MediasAdmin(admin.ModelAdmin):
    list_per_page = 50

    list_display = ('_select', '_preview', 'title', '_size', '_date',)
    list_filter = ['created_at']
    date_hierarchy = 'created_at'
    list_per_page = 25
    search_fields = ['title']

    fieldsets = (
            (None, {
                'fields': ('title', 'path',)
            }),)

    class Media:
        js = (settings.STATIC_URL + 'filebrowser/js/FB_CKEditor.js',)


    def __init__(self, *args, **kwargs):
        super(MediasAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )

    def change_view(self, request, obj=None):
        from django.core.urlresolvers import reverse
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(reverse('admin:filebrowser_file_changelist'))

    def changelist_view(self, request, extra_context={}):
        from django.contrib.admin.views.main import IS_POPUP_VAR
        if IS_POPUP_VAR in request.GET:
            req = request.GET.copy()
            if 'CKEditor' in req and 'CKEditorFuncNum' in req and 'langCode' in req:
                CKEditor, CKEditorFuncNum, langCode = \
                req.pop('CKEditor')[0], req.pop('CKEditorFuncNum')[0], req.pop('langCode')[0]
            else:
                if request.META['HTTP_REFERER']:
                    CKEditor = re.search('CKEditor=(\w+)', request.META['HTTP_REFERER']).groups()[0]
                    CKEditorFuncNum = re.search('CKEditorFuncNum=(\d+)', request.META['HTTP_REFERER']).groups()[0]
                    langCode = re.search('langCode=([a-z]{2})', request.META['HTTP_REFERER']).groups()[0]
                    url = '/admin/medias/file/?%s&CKEditor=%s&CKEditorFuncNum=%s&langCode=%s' % \
                          (request.GET.urlencode(), CKEditor, CKEditorFuncNum, langCode)
                    return HttpResponseRedirect(url)
            request.GET = req
        self.request = request
        return super(MediasAdmin, self).changelist_view(request, extra_context=extra_context)

    def add_view(self, request, form_url='', extra_context={}):
        extra_context['ref'] = request.POST['ref'] if 'ref' in request.POST else unicode(request.META.get('HTTP_REFERER', ''))
        return super(MediasAdmin, self).add_view(request, form_url, extra_context)

    def response_add(self, request, obj, post_url_continue='../%s/'):
        opts = obj._meta
        msg = _('The %(name)s "%(obj)s" was added successfully.') % \
              {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj)}

        print 2
        if request.POST.has_key("ref") and \
           urlparse.urlparse(request.POST['ref']).query and \
           request.get_host() in request.POST['ref'] and \
           not (request.POST.has_key("_continue") or request.POST.has_key("_saveasnew") or request.POST.has_key("_addanother")):
            print 1

            self.message_user(request, msg)
            change_url = reverse('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.module_name))
            potential_go_to_url = urlparse.urlparse(request.POST['ref'])
            if change_url == potential_go_to_url.path:
                query = urlparse.urlparse(request.POST['ref']).query
                return HttpResponseRedirect(change_url + '?' + query)

        return super(MediasAdmin, self).response_add(request, obj, post_url_continue)

    def save_form(self, request, form, change):
        obj = super(MediasAdmin, self).save_form(request, form, change)
        if not change:
            obj.created_by = request.user
        obj.modified_by = request.user
        return obj

    def _size(self, obj):
        return filesizeformat(obj.size)
    _size.short_description = _('Size')

    def _date(self, obj):
        if obj.created_at != obj.modified_at:
            return _('Created at <strong>%s</strong> by \
             <strong>%s </strong><br/> \
             Modified at <strong>%s</strong> by \
             <strong>%s</strong>') \
             % (obj.created_at, obj.created_by, obj.modified_at, obj.modified_by)
        else:
            return _('Created at <strong>%s</strong> by \
             <strong>%s</strong>') \
             % (obj.created_at, obj.created_by)
    _date.allow_tags = True
    _date.short_description = _('Date')

    def _select(self, obj):
        from django.contrib.admin.views.main import IS_POPUP_VAR
        if IS_POPUP_VAR in self.request.GET and self.request.GET[IS_POPUP_VAR] == '3':
            return '<span class="fb_icon"> \
            <button class="button fb_selectlink" onclick="OpenFile(\'' \
                + escapejs(obj.url) + \
            '\');return false;">' + _('Select') + '</button> \
            </span>'
        else:
            return '-'
    _select.allow_tags = True
    _select.short_description = _('Select')

    def _preview(self, obj):
        return '<a href="' + escapejs(obj.url) + '" target="_blank"> \
            <img src="' + escapejs(obj.url) + '" width="50"></a>'
    _preview.allow_tags = True
    _preview.short_description = _('Preview')

admin.site.register(File, MediasAdmin)
