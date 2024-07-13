======
Server
======

Deploy server on google app engine::

    gcloud -q app deploy app.yaml cron.yaml

See logs::

    gcloud app logs tail -s default

Local Development
=================

Run server::

    python main.py

Trigger hourly cron tasks::

    curl -H "X-Appengine-Cron: true" http://localhost:8080/scheduler/hourly
