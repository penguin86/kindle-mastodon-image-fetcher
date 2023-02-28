#!/usr/bin/env python3

""" @package docstring
A simple script that fetches the most recent non-CW image from
Mastodon, fits it to predefined screen dimensions and saves it
to a monochrome PNG file.

@author Daniele Verducci <daniele.verducci@ichibi.eu>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import requests
import json
import sys
from io import BytesIO
from PIL import Image

# CONFIG
mastodonInstanceUrl = "https://mastodon.uno"
imageFileName = "image.png"
# You can find your kindle screen resolution with the command `eips -i`
kindleResolutionWidth = 768
kindleResolutionHeight = 1024
# /CONFIG


# Get output filename from cli
if len(sys.argv) > 1:
	imageFileName = sys.argv[1]

# Obtain mastodon statuses json
statusesReqUrl = "{}/api/v1/timelines/public?only_media=true".format(mastodonInstanceUrl)
resp = requests.get(statusesReqUrl)
if resp.status_code != 200:
	print("Error fetching posts")
	exit(1)

# Get last post photo
statuses = resp.json()
attachUrl = None
for status in statuses:
	if status['sensitive']:
		continue
	if len(status['media_attachments']) > 0:
		attachUrl = status['media_attachments'][0]['url']
		if not attachUrl.endswith(".jpg"):
			continue
		break

if attachUrl == None:
	print("None of the last posts has media!")
	exit(0)

# Dowload post photo
imgBytesResp = requests.get(attachUrl)
if imgBytesResp.status_code != 200:
	print("Error downloading post photo {}".format(attachUrl))
	exit(1)

# Convert to B&W
img = Image.open(BytesIO(imgBytesResp.content))
img = img.convert(
	mode='L'	# B&W
)

# Resize to a square based on kindle screen height (needed to fit image to entire screen)
(width, height) = img.size
ratio = width / height
kindleRatio = kindleResolutionWidth / kindleResolutionHeight
cropLeft = 0
cropTop = 0
cropRight = kindleResolutionWidth
cropBottom = kindleResolutionHeight
print("Image size is {}x{}, ratio is {}, kindle ratio is {}".format(width, height, ratio, kindleRatio))
if ratio > kindleRatio:
	# Fit height
	destHeight = kindleResolutionHeight
	destWidth = width * ratio
	# Calc crop
	cropLeft = (destWidth - kindleResolutionWidth) / 2
	cropRight = cropLeft + kindleResolutionWidth
else:
	# Fit width
	destWidth = kindleResolutionWidth
	destHeight = height * (1 / ratio)
	# Calc crop
	cropTop = (destHeight - kindleResolutionHeight) / 2
	cropBottom = cropTop + kindleResolutionHeight

# Resize
img = img.resize(
	(int(destWidth), int(destHeight))
)

# Crop
img = img.crop(
	(int(cropLeft), int(cropTop), int(cropRight), int(cropBottom))
)

img.save(imageFileName, "PNG")
print("Saved {}".format(imageFileName))
