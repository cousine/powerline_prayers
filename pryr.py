# vim:fileencoding=utf-8:noet

# A prayer times segment for Powerline (https://github.com/powerline/powerline/)
# 
# This segment is based on the official weather segment for Powerline
# 
# Author: Omar Mekky (http://cousine.me)
# Date: 20-12-2014
from __future__ import (unicode_literals, division, absolute_import, print_function)

import json
import time
import math
import operator

from datetime import datetime, timedelta

from powerline.lib.url import urllib_read, urllib_urlencode
from powerline.lib.threaded import KwThreadedSegment
from powerline.segments import with_docstring

class PrayerTimeSegment(KwThreadedSegment):
    interval = 600
    current_date_time = datetime.today()
    location_geometries = {}
    prayer_times = {}

    @staticmethod
    def key(location_query=None, timezone=2, method=5, **kwargs):
        return (location_query, timezone, method)

    def get_geometry(self, location_query):
        try:
            return self.location_geometries[location_query]
        except KeyError:
            if location_query is None:
                self.error('No location specified')
            else:
		location = location_query.split(',')
		query_data = {
			'address':  location[0],
			'region':   location[1],
			'sensor':   'false'
		}

		location_data = json.loads(urllib_read('http://maps.google.com/maps/api/geocode/json?' + urllib_urlencode(query_data)))
		if location_data['results']:
		    location = ','.join((
			str(location_data['results'][0]['geometry']['location']['lat']), 
			str(location_data['results'][0]['geometry']['location']['lng'])
		    ))

		    self.location_geometries[location_query] = geometry = location
		    return geometry
		else:
		    self.location_geometries['cairo, eg'] = geometry = '30.0444196,31.2357116'
		    return geometry

    def get_prayer_times(self, prayer_tuple):
        timestamp = long(math.ceil(time.time()))

        if (datetime.fromtimestamp(timestamp) - self.current_date_time).days == 0 and self.prayer_times:
            return self.prayer_times

	geometry = self.get_geometry(prayer_tuple[0])

	if geometry is not None:
	    geometry = geometry.split(',')
	else:
	    return None

        query_data = {
            'latitude': geometry[0],
            'longitude': geometry[1],
            'timezone': prayer_tuple[1],
            'method': prayer_tuple[2]
        }

        raw_response = urllib_read('http://api.aladhan.com/timings/{0}?'.format(timestamp) + urllib_urlencode(query_data))

        if not raw_response:
            self.error('Failed to get response')
            return None

        response = json.loads(raw_response)
        try:
            for prayer, rtime in response['data']['timings'].iteritems():
                ptime = datetime.strptime(rtime, '%H:%M')
                self.prayer_times[prayer] = ptime.replace(self.current_date_time.year, self.current_date_time.month, self.current_date_time.day)
        except (KeyError, ValueError):
            self.exception('Al Adhan returned a malformed or unrexpected response: {0}', repr(raw_response))
            return None

        self.prayer_times = sorted(self.prayer_times.items(), key=operator.itemgetter(1))

	return self.prayer_times

    def calculate_next_prayer(self, ptime, time_now, prayer):
	delta_time = ptime - time_now
	hours, remainder = divmod(delta_time.seconds, 3600)
	minutes, seconds = divmod(remainder, 60)

	if prayer == "Maghrib" or prayer == "Isha":
	    icon_name = "dark"
	else:
	    icon_name = "light"

	return (prayer, hours, minutes, icon_name)

    def compute_state(self, prayer_tuple):
        time_now = datetime.now()
        present_prayer = None

        if self.get_prayer_times(prayer_tuple):
            for prayer, ptime in self.prayer_times:
                if time_now >= ptime:
                    present_prayer = prayer
                elif time_now < ptime and present_prayer:
		    return self.calculate_next_prayer(ptime, time_now, prayer)
		elif (self.current_date_time - time_now).days != 1:
		    self.current_date_time = time_now + timedelta(days= 1)
		else:
		    self.calculate_next_prayer(self.prayer_times["Fajr"], time_now, "Fajr")
        else:
            return None

    def render_one(self, prayer_time, icons=None, **kwargs):
        if not prayer_time:
            return None
        
        prayer, hours, minutes, icon_name = prayer_time

        if icons:
            if icon_name in icons:
                icon = icons[icon_name]
            else:
                icon = ''
        else:
            icon = ''

        if hours == 0 and minutes < 30:
            highlight_group = ['prayer_times_critical', 'prayer_times']
        elif hours == 0 and minutes >= 30:
            highlight_group = ['prayer_times_warning', 'prayer_times']
        else:
            highlight_group = ['prayer_times']

        prayer_time_countdown = "{0} -{1:02}:{2:02}".format(prayer, hours, minutes)

        return [
            {
                'contents': icon + ' ',
                'highlight_group': highlight_group,
                'divider_highlight_group': 'background:divider'
            },
            {
                'contents': prayer_time_countdown,
                'highlight_group': highlight_group,
                'divider_highlight_group': 'background:divider'
            }
        ]

prayer_time = with_docstring(PrayerTimeSegment(), 
''' Return a countdown to the next prayer from Al Adhan (http://aladhan.com)

:param str location_query:
    location query for your current location, e.g. ``cairo, eg``
:param int timezone:
    your timezone in int, valid values are from -12 to 12
:param int method:
    prayer time calculation method, valid values are from 0 to 7 (for more information check http://aladhan.com/rest-api)

Divider highlight group used: ``background:divider``

Highlight groups used: ``prayer_times``, ``prayer_times_critical``, ``prayer_times_warning``
'''
)
