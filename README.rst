==========
nest-stats
==========

Nest logger
===========

Deploy event logger. The last line of output will be the URL to use in
the push subscription::

  # Deploy function
  gcloud functions deploy nest-logger --gen2 --runtime=python312 --source=functions --entry-point=process_webhook --trigger-http --allow-unauthenticated

Inspect cloud function log::

  gcloud functions logs read --gen2 --limit=5 nest-logger

Create a push subscription. Get URL when you deploy event logger::

  gcloud pubsub subscriptions create nest-events --topic=projects/sdm-prod/topics/<topic> --push-endpoint=<url>

Weather logger
==============

Create a cloud scheduler job that triggers once an hour and publishes on
``hourly_events`` topic.

Deploy::

  gcloud functions deploy hourly-events --gen2 --runtime=python312 --source=functions --entry-point=hourly_events --trigger-topic=hourly-weather

Manual trigger for testing::

  gcloud pubsub topics publish hourly-weather --message=now

The weather logger stores the api key in secrets manager, so service accounts
must have ``Secret Manager Secret Accessor``: ``developer.gserviceaccount.com``
and ``appspot.gserviceaccount.com``.

Inspect cloud function log::

  gcloud functions logs read --gen2 --limit=5 hourly-events

For debugging, limit the number of retries, not sure this works::

  gcloud pubsub topics create nest-events-dead-letter
  gcloud pubsub subscriptions update nest-events --max-delivery-attempts=5 --dead-letter-topic=projects/<project-id>/topics/nest-events-dead-letter

Things that did not work
========================

Use pubsub functionality in cloud functions, but does not let you
specify topic in another project::

  gcloud functions deploy nest-stats --gen2 --runtime=python312 --source=. --entry-point=subscribe --trigger-topic=<topic>
