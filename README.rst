Athena
===

**Athena** is a web application that creates geo-quizzes. Athena's interactive maps are created using the Google Maps API and Google Fusion Tables.  Athena can also quiz you on capitals via text message.

Quickstart:
===

Install django-tinymce:

    $ pip install django-tinymce

Add tinymce to INSTALLED_APPS in settings.py for your project:

    INSTALLED_APPS = (
        ...
        'tinymce',
    )

Add tinymce.urls to urls.py for your project:

    urlpatterns = patterns('',
        ...
        (r'^tinymce/', include('tinymce.urls')),
    )

In your code:

    from django.db import models
    from tinymce.models import HTMLField

    class MyModel(models.Model):
        ...
        content = HTMLField()

**django-tinymce** uses staticfiles so everything should work as expected, different use cases (like using widget instead of HTMLField) and other stuff is available in documentation.

Documentation:
===
http://django-tinymce.readthedocs.org/

Support and updates:
===
You can contact me directly at aljosa.mohorovic@gmail.com, track updates at https://twitter.com/maljosa or use github issues.
Be persistent and bug me, I often find myself lost in time so ping me if you're still waiting for me to answer.

License (and related information):
===
Originally written by Joost Cassee.

This program is licensed under the MIT License (see LICENSE.txt)