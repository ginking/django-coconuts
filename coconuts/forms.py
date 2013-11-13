# -*- coding: utf-8 -*-
#
# django-coconuts
# Copyright (c) 2008-2013, Jeremy Lainé
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     1. Redistributions of source code must retain the above copyright notice,
#        this list of conditions and the following disclaimer.
#
#     2. Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

from operator import itemgetter

from django import forms
from django.forms.formsets import formset_factory, BaseFormSet
from django.utils.translation import ugettext_lazy as _

from coconuts.models import Share, OWNERS, PERMISSIONS, PERMISSION_NAMES

class AddFileForm(forms.Form):
    upload = forms.FileField()

class AddFolderForm(forms.Form):
    name = forms.CharField()

class PhotoForm(forms.Form):
    SIZE_CHOICES = (
        (128, '128'),
        (800, '800'),
        (1024, '1024'),
        (1280, '1280'),
    )

    size = forms.TypedChoiceField(choices=SIZE_CHOICES, coerce=int)

class OwnerField(forms.ChoiceField):
    def __init__(self, **kwargs):
        choices = [('', '')]
        for klass, key in OWNERS:
            opts = []
            for obj in klass.objects.all().order_by(key):
                opts.append(("%s:%s" % (klass.__name__.lower(), getattr(obj, key)), obj))
            if len(opts):
                choices.append((klass.__name__, opts))
        super(OwnerField, self).__init__(choices=choices, **kwargs)

class ShareForm(forms.ModelForm):
    class Meta:
        model = Share
        exclude = ('path', 'access')

class ShareAccessForm(forms.Form):
    def __init__(self, **kwargs):
        super(ShareAccessForm, self).__init__(**kwargs)
        self.fields['owner'] = OwnerField(label=_('Who?'))
        for perm in [ x[0] for x in sorted(PERMISSIONS.items(), key=itemgetter(1))]:
            self.fields[perm] = forms.BooleanField(required=False, label=PERMISSION_NAMES[perm])

class BaseShareAccessFormSet(BaseFormSet):
    def clean(self):
        """Merge permissions for each owner."""
        unique = {}
        for form in self.forms:
            data = form.clean()
            if not form.is_valid():
                raise forms.ValidationError, u'An error occured.'
            if data:
                owner = data['owner']
                if unique.has_key(owner):
                    for perm in PERMISSIONS:
                        if data[perm]: unique[owner][perm] = data[perm]
                else:
                    unique[owner] = data
        return unique.values()

ShareAccessFormSet = formset_factory(ShareAccessForm, formset=BaseShareAccessFormSet)

