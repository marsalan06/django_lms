import datetime
import os
import random
import string

from django.utils.text import slugify


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


def unique_slug_generator(instance, new_slug=None):
    """
    This is for a Django project and it assumes your instance
    has a model with a slug field and a title character (char) field.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        if hasattr(instance, "code") and instance.code:
            course_code = slugify(instance.code)
        else:
            # Incorporate the course title into the slug
            course_code = slugify(instance.course.code)
        title = slugify(instance.title)
        if hasattr(instance, "course") and instance.course:
            org = slugify(instance.course.program.organization)
        else:
            org = slugify(instance.program.organization)
        slug = f"{course_code}-{title}-{org}"

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
            slug=slug, randstr=random_string_generator(size=4)
        )
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug
