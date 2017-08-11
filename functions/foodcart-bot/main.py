#!/bin/which python3

import requests
import dateutil.parser
from datetime import datetime, timedelta
import logging
import pytz
import inflect
import os

# set up logging
logger = logging.getLogger('CartBot')
logger.setLevel(logging.DEBUG)
if not len(logger.handlers):
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - ' +
                                  '%(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

url = os.getenv('foodcart_url', 'https://www.seattlefoodtruck.com/api/events?page=1&for_locations=40&' +
                'with_active_trucks=true&include_bookings=true&with_booking_status=approved')
slack_webhook = os.environ['slack_webhook_url']


class Foodcart:
    """Food cart booking object"""

    def __init__(self, name, style):
        self.name = name
        self.style = style
        self.url = ""
        self.photo = None
        self.start_time = ""
        self.end_time = ""


def parse_date(datestring):
    """ Parse an ISO8601 formatted string to a datetime object """
    return dateutil.parser.parse(datestring)


def parse_booking(booking):
    """Parse a booking object and return a Foodcart object"""
    logging.debug("Received a booking of %s" % booking)
    cart = Foodcart(booking['name'], booking['food_categories'])

    if 'id' in booking:
        cart.url = "https://seattlefoodtruck.com/food-trucks/%s" % booking['id']
    if 'featured_photo' in booking:
        cart.photo = booking['featured_photo']
    return cart


def main():
    """ Main loop, fetching today's carts and sending to Slack """
    logger.debug("Fetching url %s" % url)
    r = requests.get(url)

    # abort with error if we don't get a valid response back
    if not r.status_code == requests.codes.ok:
        r.raise_for_status()

    dat = r.json()

    # set our timezone to Pacific, as we expect to be working in UTC
    tz = pytz.timezone('US/Pacific')

    tomorrow = datetime.utcnow().replace(tzinfo=tz) + timedelta(days=1)
    yesterday = datetime.utcnow().replace(tzinfo=tz) - timedelta(days=1)

    # only work on the carts due to arrive today
    entries = [k for k in dat['events'] if tomorrow.date() > parse_date(k['start_time']).date() >
               yesterday.date()]

    # parse out Foodcart objects from each of the bookings
    carts = {}
    for i in entries:
        for k in i['bookings']:
            logger.debug("Working on booking: %s" % k)
            this_cart = parse_booking(k['truck'])
            this_cart.start_time = parse_date(i['start_time'])
            this_cart.end_time = parse_date(i['end_time'])
            carts[this_cart.name] = this_cart

    send_to_slack(carts)

    return carts


def send_to_slack(listings):
    """ Send a collection of foodcarts to Slack"""
    # Today's menu:
    #  Style, style - Name (hyperlinked)
    #  Style, style - Name (hyperlinked)
    #  Style, style - Name (hyperlinked)
    #  Bon Appetit!
    # if len(0)
    #   There don't appear to be any bookings today!
    p = inflect.engine()
    params = {
        "username": "CartBot",
        "icon_emoji": ":fork_and_knife:",
        "text": "%s food %s on site today." % (p.number_to_words(len(listings)).capitalize(),
                                               p.plural("cart", len(listings))),
    }
    attachments = []
    for i in listings.values():
        attachment = {
            "fallback": "%s|%s - Serving %s." % (i.name, i.url, ', '.join([str(x) for x in i.style])),
            "color": "#36a64f",
            "title": i.name,
            "title_link": i.url,
            "fields": [
                {"title": "Service Starts",
                 "value": datetime.strftime(i.start_time, "%r"),
                 "short": True
                 },
                {"title": "Service Ends",
                 "value": datetime.strftime(i.end_time, "%r"),
                 "short": True
                 },
                {
                    "title": "Cuisine",
                    "value": ', '.join([str(x) for x in i.style]),
                    "short": True
                },
            ],
        }
        if i.photo is not None:
            attachment['thumb_url'] = "https://s3-us-west-2.amazonaws.com/seattlefoodtruck-uploads-prod/%s" % i.photo
        attachments.append(attachment)
    params['attachments'] = attachments
    headers = {'content-type': 'application/json'}
    # slack_api = 'https://slack.com/api/chat.postMessage'
    r = requests.post(slack_webhook, json=params, headers=headers)
    if not r.status_code == requests.codes.ok:
        r.raise_for_status()
    return


if __name__ == "__main__":
    dat = main()
    logger.info("found %s carts." % (len(dat)))


def lambda_handler(event=None, context=None):
    """ main Lambda event handling loop """
    main()
