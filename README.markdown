Powerline Prayer Times
======================

**Author:** [Omar Mekky](http://cousine.me) - [iam@cousine.me](mailto: iam@cousine.me)

**Powerline Prayer Times is a [Powerline](https://github.com/powerline/powerline)
3rd party segment to show a countdown timer for the next due islamic prayer using
[Al Adhan's](http://aladhan.com) REST API**

Installation
------------

There isn't any automated method to install 3rd party segments for Powerline, however
by following the steps below you can manually install Prayer Times:

* Follow Powerline's [Quick setup guide](https://powerline.readthedocs.org/en/master/configuration.html#quick-setup-guide) to create the default configrations and folders
* Under your `~/.config/powerline` directory, create a `segments` directory to hold 3rd party segments
* Copy `pryr.py` to the newly created `segments` directory
* Using your favorite editor open up `~/.config/powerline/config.json` and add the lines below to the `common` section:
```
"paths": [
  "~/.config/powerline/segments"
]
```
* Now open `~/.config/powerline/themes/powerline.json` and add the following lines right after the last section:
```
,"pryr.prayer_time": {
  "args": {
    "icons": {
      "light":       "☼",
      "dark":        "☾"
    }
  }
}
```
* Next open up `~/.config/powerline/colorschemes` and add the following lines to the end of the `groups` section:
```
,"prayer_times":              { "fg": "green", "bg": "gray2", "attr": [] },
"prayer_times_critical":     { "fg": "red", "bg": "gray2", "attr": [] },
"prayer_times_warning":    { "fg": "brightyellow", "bg": "gray2", "attr": [] }
```
* Finally add `Prayer times` to your `Powerline` theme:
```
  {
    "function": "pryr.prayer_time",
    "priority": 50,
    "args": {
      "location_query": "cairo, eg",
      "timezonestring": "Africa/Cairo",
      "method": 5
    }
  }
```

Screenshot
----------

![Preview](https://raw.githubusercontent.com/cousine/powerline_prayers/master/preview.png)
