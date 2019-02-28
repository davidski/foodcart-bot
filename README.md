FoodCart-Bot
================

Python based AWS Lambda function for posting the food carts scheduled to 
be on-site today to a Slack channel.

When triggered, this function polls the Seattle Food Cart API for the 
food carts booked for today. These bookings are parsed into custom objects 
and posted to Slack via a webhook.

Environment Variables
------------------------------

+ slack_webhook_url - Full URL for a webhook to post to your Slack team.
+ foodcart_url - Optional URL to the API endpoint to retrieve today's bookings.
+ attachment_color - Optional color to use for attachments when posting to Slack.
+ default_truck_image_rul - Optional URL to an image to use when a image of the foodcart is not available.

Deployment
----------

The included [Makefile](./Makefile) will build a ZIP file, including all 
dependencies, which can be deployed to AWS Lambda. A periodic CloudWatch event to fire the bot once a 
day is the most straightforward mechanism to run this code automatically.

Contributing
============

This project is governed by a [Code of Conduct](./CODE_OF_CONDUCT.md). By 
participating in this project you agree to abide by these terms.

License
=======

The [MIT License](LICENSE) applies.
