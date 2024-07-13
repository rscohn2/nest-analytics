======
Server
======

Deploy server on google app engine::

    gcloud app deploy app.yaml cron.yaml

Local Development
=================

Run server::

    python main.py

Trigger hourly cron tasks::

    curl -H "X-Appengine-Cron: true" http://localhost:8080/scheduler/hourly
