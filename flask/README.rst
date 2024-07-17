======
Server
======

Deploy server on google app engine::

    # Collector service for climate data
    gcloud -q app deploy collector.yaml
    # User interface at climate.rcohn.us
    gcloud -q app deploy portal.yaml
    # trigger time driven events
    gcloud -q app deploy cron.yaml
    # connects custom domains to services
    gcloud -q app deploy dispatch.yaml

See logs::

    gcloud app logs tail -s collector
    gcloud app logs tail -s portal

Local Development
=================

Run server::

    python portal_main.py
    python collector_main.py

Trigger hourly cron tasks::

    curl -H "X-Appengine-Cron: true" http://localhost:8080/scheduler/hourly
