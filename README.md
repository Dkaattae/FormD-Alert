# FormD-Alert
get new form d from SEC form d rss feed, store into Redis, read form d, and enrich information from my current database. send out email alert. 

# Steps
The Step-by-Step Logic
Stage 1: The "Gatherer" (Every 60 Minutes)
Trigger: A cron job running every hour.

Action: Fetches the SEC Form D RSS Feed.

Redis Check: Stores the Accession Number as a key. If the key exists, ignore it. If it’s new, add it to a Redis List called daily_queue.

Stage 2: The "Enricher" (Daily at 6:00 AM)
Trigger: A separate cron job that kicks off your main processing script.

Action: 1.  Read XML: Pops all entries from the daily_queue. For each, it constructs the URL for the primary_doc.xml.
2.  Extract Data: Pulls relatedPersonsList (Owners), isAmendment, and totalAmountSold.
3.  Cross-Reference (BQ): Queries your BigQuery adv_historical table using the CIK.
* Match Found: Retrieves the Manager's CRD and current Auditor.
* No Match: Tags the fund as "Brand New Manager."

Stage 3: The "Alert" (Final Output)
Action: Formats the enriched data into a single summary email or individual alerts using a template.

Clearing: Clears the Redis daily_queue but keeps the Accession Number keys (with a 48h TTL) to ensure no duplicates in the next hour's gatherer.
