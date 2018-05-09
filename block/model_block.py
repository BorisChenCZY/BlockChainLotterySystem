# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Block(models.Model):
    block_id = models.IntegerField(blank=True, null=True)
    block_hash = models.TextField(blank=True, null=True)
    pre_hash = models.TextField(blank=True, null=True)
    class Meta:
        app_label = 'block'
        db_table = 'block'


class BlockInfo(models.Model):
    block_id = models.IntegerField(blank=True, null=True)
    vote_id = models.IntegerField(blank=True, null=True)
    public_key = models.TextField(blank=True, null=True)

    class Meta:
        app_label = 'block'
        db_table = 'block_info'


class VoteInfo(models.Model):
    vote_id = models.IntegerField(blank=True, null=True)
    void_content = models.IntegerField(blank=True, null=True)

    class Meta:
        app_label = 'block'
        db_table = 'vote_info'
