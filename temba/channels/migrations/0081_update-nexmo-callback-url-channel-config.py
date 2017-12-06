# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-30 15:40
from __future__ import unicode_literals

import json

from django.conf import settings
from django.db import migrations
from django.urls import reverse

from temba.orgs.models import Org, NEXMO_KEY, NEXMO_SECRET, NEXMO_APP_ID, NEXMO_APP_PRIVATE_KEY
from temba.utils.nexmo import NexmoClient


class Migration(migrations.Migration):

    dependencies = [
        ('channels', '0080_fix_sql_func'),
    ]

    def update_nexmo_channels_config(apps, schema_editor):
        Channel = apps.get_model('channels', 'Channel')

        if settings.IS_PROD:
            nexmo_channels = Channel.objects.filter(channel_type='NX').exclude(org=None)

            updated = []
            for channel in nexmo_channels:
                try:
                    org = Org.objects.get(pk=channel.org_id)
                    org_config = org.config_json()
                    app_id = org_config[NEXMO_APP_ID]
                    config = {Channel.CONFIG_NEXMO_APP_ID: app_id,
                              Channel.CONFIG_NEXMO_APP_PRIVATE_KEY: org_config[NEXMO_APP_PRIVATE_KEY],
                              Channel.CONFIG_NEXMO_API_KEY: org_config[NEXMO_KEY],
                              Channel.CONFIG_NEXMO_API_SECRET: org_config[NEXMO_SECRET]}

                    client = NexmoClient(config[Channel.CONFIG_NEXMO_API_KEY],
                                         config[Channel.CONFIG_NEXMO_API_SECRET],
                                         config[Channel.CONFIG_NEXMO_APP_ID],
                                         config[Channel.CONFIG_NEXMO_APP_PRIVATE_KEY])

                    receive_url = "https://" + org.get_brand_domain() + reverse('courier.nx',
                                                                                args=[channel.uuid, 'receive'])

                    client.update_nexmo_number(channel.country, channel.address, receive_url, app_id)

                    channel.config = json.dumps(config)
                    channel.save()

                    updated.append(channel.id)
                except Exception:
                    pass

    operations = [
        migrations.RunPython(update_nexmo_channels_config)
    ]