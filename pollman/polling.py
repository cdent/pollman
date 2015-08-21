# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from oslo_log import log
from oslo_utils import timeutils
import requests

from ceilometer.agent import plugin_base as plugin
from ceilometer import sample

APPID = os.environ.get('WEATHER_APP_ID')
UNIT = 'metric'
WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather?id=%(id)s&APPID=%(appid)s&units=%(unit)s'
LOG = log.getLogger(__name__)


class PollmanPollster(plugin.PollsterBase):
    """A generic external ceilometer plugin."""

    NAME = 'weather.temperature'

    def __init__(self):
        super(PollmanPollster, self).__init__()

    @property
    def default_discovery(self):
        return 'pollman'

    def get_samples(self, manager, cache, resources):

        for resource in resources:
            url = WEATHER_URL % {'id': resource,
                                 'appid': APPID,
                                 'unit': UNIT}
            data = requests.get(url).json()
            LOG.debug('got %s from %s', data, url)
            yield sample.Sample(
                name=self.NAME,
                type=sample.TYPE_GAUGE,
                unit='C',
                volume=data['main']['temp'],
                resource_id=str(resource),
                user_id='pollman',
                project_id='pollman',
                resource_metadata={'location': data['name'],
                                   'country': data['sys']['country']},
                timestamp=timeutils.utcnow().isoformat(),
            )
