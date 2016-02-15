from __future__ import unicode_literals

from django.core.exceptions import MultipleObjectsReturned
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language

from apps.core.exceptions import DMPwerkzeugException
from apps.projects.models import Project


class GroupManager(models.Manager):

    def get_next(self, last_group):
        groups = self \
            .filter(order__gte=last_group.order) \
            .filter(subsection__order__gte=last_group.subsection.order) \
            .filter(subsection__section__order__gte=last_group.subsection.section.order)

        for i, group in enumerate(groups):
            if group == last_group:
                print (i, len(groups))
                if i + 1 >= len(groups):
                    raise Group.DoesNotExist
                else:
                    return groups[i + 1]


@python_2_unicode_compatible
class Interview(models.Model):

    project = models.ForeignKey(Project, related_name='interviews')

    title = models.CharField(max_length=256)

    completed = models.BooleanField()
    current_group = models.ForeignKey('Group', null=True)

    created = models.DateTimeField(editable=False)
    updated = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = now()

        self.updated = now()
        super(Interview, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('project', 'updated')
        verbose_name = _('Interview')
        verbose_name_plural = _('Interviews')


@python_2_unicode_compatible
class Section(models.Model):

    slug = models.SlugField()
    order = models.IntegerField(null=True)

    title_en = models.CharField(max_length=256)
    title_de = models.CharField(max_length=256)

    @property
    def title(self):
        if get_language() == 'en':
            return self.title_en
        elif get_language() == 'de':
            return self.title_de
        else:
            raise DMPwerkzeugException('Language is not supported.')

    def __str__(self):
        return self.slug

    class Meta:
        ordering = ('order',)
        verbose_name = _('Section')
        verbose_name_plural = _('Sections')


@python_2_unicode_compatible
class Subsection(models.Model):

    slug = models.SlugField()
    order = models.IntegerField(null=True)

    title_en = models.CharField(max_length=256)
    title_de = models.CharField(max_length=256)

    section = models.ForeignKey(Section, related_name='subsections')

    @property
    def title(self):
        if get_language() == 'en':
            return self.title_en
        elif get_language() == 'de':
            return self.title_de
        else:
            raise DMPwerkzeugException('Language is not supported.')

    def __str__(self):
        return self.section.slug + '.' + self.slug

    class Meta:
        ordering = ('section__order', 'order')
        verbose_name = _('Subsection')
        verbose_name_plural = _('Subsections')


@python_2_unicode_compatible
class Group(models.Model):

    objects = GroupManager()

    slug = models.SlugField()
    order = models.IntegerField(null=True)

    title_en = models.CharField(max_length=256)
    title_de = models.CharField(max_length=256)

    subsection = models.ForeignKey(Subsection, related_name='groups')

    @property
    def title(self):
        if get_language() == 'en':
            return self.title_en
        elif get_language() == 'de':
            return self.title_de
        else:
            raise DMPwerkzeugException('Language is not supported.')

    def __str__(self):
        return self.subsection.section.slug + '.' + self.subsection.slug + '.' + self.slug

    class Meta:
        ordering = ('subsection__section__order', 'subsection__order',  'order',)
        verbose_name = _('Group')
        verbose_name_plural = _('Group')


@python_2_unicode_compatible
class Question(models.Model):

    ANSWER_TYPE_CHOICES = (
        ('bool', 'Bool'),
        ('string', 'String'),
        ('list', 'List'),
        ('integer', 'Integer'),
        ('float', 'Float')
    )

    WIDGET_TYPE_CHOICES = (
        ('text', 'Text'),
        ('textarea', 'Textarea'),
        ('checkbox', 'Checkbox'),
        ('radio', 'Radio button'),
        ('select', 'Select'),
        ('multiselect', 'Multiselect'),
        ('slider', 'Slider'),
        ('list', 'List'),
    )

    slug = models.SlugField()
    order = models.IntegerField(null=True)

    group = models.ForeignKey(Group, related_name='questions')

    text_en = models.TextField()
    text_de = models.TextField()

    answer_type = models.CharField(max_length=12, choices=ANSWER_TYPE_CHOICES)
    widget_type = models.CharField(max_length=12, choices=WIDGET_TYPE_CHOICES)

    options = models.ManyToManyField('Option', blank=True)

    @property
    def text(self):
        if get_language() == 'en':
            return self.text_en
        elif get_language() == 'de':
            return self.text_de
        else:
            raise DMPwerkzeugException('Language is not supported.')

    def __str__(self):
        return str(self.group) + '.' + self.slug

    class Meta:
        ordering = ('group__subsection__section__order', 'group__subsection__order',  'group__order', 'order')
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')


@python_2_unicode_compatible
class Option(models.Model):

    key = models.SlugField()

    text_en = models.CharField(max_length=256)
    text_de = models.CharField(max_length=256)

    @property
    def text(self):
        if get_language() == 'en':
            return self.text_en
        elif get_language() == 'de':
            return self.text_de
        else:
            raise DMPwerkzeugException('Language is not supported.')

    def __str__(self):
        return self.text

    class Meta:
        ordering = ('key', )
        verbose_name = _('Option')
        verbose_name_plural = _('Options')


# @python_2_unicode_compatible
# class Jump(models.Model):

#     CONDITION_TYPE_CHOICES = (
#         ('>', 'greater (>)'),
#         ('>=', 'greater equal (>=)'),
#         ('<', 'lesser (<)'),
#         ('<=', 'lesser equal (<=)'),
#         ('==', 'equal (==)'),
#         ('!=', 'not equal (!=)'),
#     )

#     condition_question = models.ForeignKey(Question)
#     condition_type = models.CharField(max_length=2, choices=CONDITION_TYPE_CHOICES)
#     condition_value = models.CharField(max_length=256)

#     target = models.ForeignKey(Question, related_name='jumps')

#     def __str__(self):
#         return self.condition_question

#     class Meta:
#         ordering = ('condition_question', 'condition_value')
#         verbose_name = _('Jump')
#         verbose_name_plural = _('Jumps')


@python_2_unicode_compatible
class Answer(models.Model):

    interview = models.ForeignKey('Interview', related_name='answers')
    question = models.ForeignKey('Question')
    value = models.TextField()

    created = models.DateTimeField(editable=False)
    updated = models.DateTimeField(editable=False)

    @property
    def section_slug(self):
        return self.question.group.subsection.section.slug

    @property
    def subsection_slug(self):
        return self.question.group.subsection.slug

    @property
    def group_slug(self):
        return self.question.group.slug

    @property
    def question_slug(self):
        return self.question.slug

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = now()

        self.updated = now()
        super(Answer, self).save(*args, **kwargs)

    def __str__(self):
        return self.question.slug

    class Meta:
        ordering = ('interview', 'question')
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')
