FoodCart-Bot
================

Python based AWS Lambda function for posting the food cart's scheduled to 
be on-site today to a Slack channel.

When triggered, this function polls the Seattle Food Cart API for the 
booked food carts for the day. These bookings are parsed into custom objects 
and posted to Slack via a webhook.

Environment Variables
------------------------------

+ slack_webhook_url - Full URL for a webhook to post to your slack team.
+ foodcart_url - Optional URL to the API endpoint to retrieve today's bookings.
+ attachment_color - Optional color to use for attachments when posting to Slack.

Deployment
----------

The included [Makefile](./Makefile) will build a ZIP file which can be 
deployed to AWS Lambda. This ZIP file will include all dependencies.

For executing, using a periodic CloudWatch event to fire the bot once a 
day is one of the most straightforward mechanisms.

Contributing
============

This project is governed by a [Code of Conduct](./CODE_OF_CONDUCT.md). By 
participating in this project you agree to abide by these terms.

License
=======

The [MIT License](LICENSE) applies.
