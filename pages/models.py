# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Mailbox(models.Model):
    id = models.IntegerField(primary_key=True)
    to_user = models.ForeignKey('User', on_delete=models.DO_NOTHING, related_name='touser')
    from_user = models.ForeignKey('User', on_delete=models.DO_NOTHING)
    text = models.TextField(max_length=500)
    datetime = models.DateTimeField()
    is_read = models.IntegerField()
    subject = models.CharField(max_length=75)

    class Meta:
        managed = False
        db_table = 'mailbox'
        unique_together = (('id', 'to_user', 'from_user'),)


class Post(models.Model):
    id = models.IntegerField(primary_key=True)
    text = models.TextField()
    is_edit = models.IntegerField()
    last_edit = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey('User', models.DO_NOTHING)
    theme = models.ForeignKey('Theme', on_delete=models.CASCADE)
    datetime = models.DateTimeField(blank=True)

    class Meta:
        managed = False
        db_table = 'post'
        unique_together = (('id', 'user', 'theme'),)


class RegistrationForm(models.Model):
    id = models.IntegerField(primary_key=True)
    email = models.CharField(max_length=254)
    nickname = models.CharField(max_length=15)
    password_hash = models.CharField(max_length=64)
    time = models.BigIntegerField()
    confirm_hash = models.CharField(max_length=64)
    is_complete = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'registration_form'


class Section(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=75)

    class Meta:
        managed = False
        db_table = 'section'


class Session(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey('User', models.DO_NOTHING)
    hash = models.CharField(max_length=64)
    time = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'session'
        unique_together = (('id', 'user'),)


class Theme(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=75)
    user = models.ForeignKey('User', models.DO_NOTHING)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    datetime = models.DateTimeField(blank=True)

    class Meta:
        managed = False
        db_table = 'theme'
        unique_together = (('id', 'user', 'section'),)


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    email = models.CharField(unique=True, max_length=254)
    nickname = models.CharField(unique=True, max_length=15)
    password_hash = models.CharField(max_length=64)
    is_admin = models.IntegerField()
    registration_date = models.DateField()
    last_activity = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'user'
