"""
Sample program for hikvision api.
"""

import logging
import pyhik.hikvision as hikvision
import datetime
import shutil
import requests

dvr1 = '192.168.15.42'
urlBase= '/ISAPI/Streaming/channels/'
streamType ='01'
parameter = '/picture?snapShotImageType=JPEG'
login = 'admin'
passwd = 'Esiexata2017'

line = 0
lineMov = 0

logging.basicConfig(filename='out.log', filemode='w', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

_LOGGING = logging.getLogger(__name__)

debug = False

dateStart = datetime.datetime.now()


class HikCamObject(object):
    """Representation of HIk camera."""

    def __init__(self, url, port, user, passw):
        """initalize camera"""

        # Establish camera
        self.cam = hikvision.HikCamera(url, port, user, passw)

        self._name = self.cam.get_name
        self.motion = self.cam.current_motion_detection_state

        # Start event stream
        self.cam.start_stream()

        self._event_states = self.cam.current_event_states
        self._id = self.cam.get_id

        print('Sistema iniciado com sucesso: {}'.format(self._name))

        if debug is True:
            print('NAME: {}'.format(self._name))
            print('ID: {}'.format(self._id))
            print('{}'.format(self._event_states))
            print('Motion Dectect State: {}'.format(self.motion))

    @property
    def sensors(self):
        """Return list of available sensors and their states."""
        return self.cam.current_event_states

    def get_attributes(self, sensor, channel):
        """Return attribute list for sensor/channel."""
        return self.cam.fetch_attributes(sensor, channel)

    def stop_hik(self):
        """Shutdown Hikvision subscriptions and subscription thread on exit."""
        self.cam.disconnect()

    def flip_motion(self, value):
        """Toggle motion detection"""
        if value:
            self.cam.enable_motion_detection()
        else:
            self.cam.disable_motion_detection()


class HikSensor(object):
    """ Hik camera sensor."""

    def __init__(self, sensor, channel, cam):
        """Init"""
        self._cam = cam
        self._name = "{} {} {}".format(self._cam.cam.name, sensor, channel)
        self._id = "{}.{}.{}".format(self._cam.cam.cam_id, sensor, channel)
        self._sensor = sensor
        self._channel = channel

        self._cam.cam.add_update_callback(self.update_callback, self._id)

    def _sensor_state(self):
        """Extract sensor state."""
        return self._cam.get_attributes(self._sensor, self._channel)[0]

    def _sensor_last_update(self):
        """Extract sensor last update time."""
        return self._cam.get_attributes(self._sensor, self._channel)[3]

    @property
    def name(self):
        """Return the name of the Hikvision sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return an unique ID."""
        return '{}.{}'.format(self.__class__, self._id)

    @property
    def is_on(self):
        """Return true if sensor is on."""
        return self._sensor_state()



    def update_callback(self, msg):
        global lineMov
        lineMov += 1
        # """ get updates. """
        # print('Callback: {}'.format(msg))

        # print('{}:{} @ {}'.format(self.name, self._sensor_state(), self._sensor_last_update()))

        if debug is True:
            print("name", self._name)
            print("sensor_state", self._sensor_state())
            print("sensor", self._sensor)
            print("sensor_last_update", self._sensor_last_update())
            print("canal", self._channel)

        if self._sensor == 'Line Crossing' and self._channel is 3 and self._sensor_state() is True:
            global line
            line += 1
            print("Atençao cruzamento de linha detectado !!!!!!!!!!!!!!!!!!!!!!!")
            print("foi cruzado a linha na camera {} por {} vezes desde {}".format(self._channel, line, dateStart))
            _LOGGING.debug("cruzamento de linha detectado na camera ")
            save_Snapshot(self,self._sensor,dvr1, login, passwd, self._channel)

        elif self._sensor == 'Motion' and self._sensor_state() is True:
            _LOGGING.debug("movimento detectado na camera: ")
            print("movimento detectado ##########################")
            save_Snapshot(self,self._sensor, dvr1, login, passwd, self._channel)


        # print(datetime.datetime.now())
        # horario = datetime.datetime.now()
        # print ("diferenca tempo:",horario - self._sensor_last_update())


def save_Snapshot(self,name,dvr, login, passwd, ch):
    url ='http://{}{}{}{}{}'.format(dvr,urlBase,ch,streamType,parameter)
    #print (url)
    response = requests.get(url, auth=(login, passwd), stream=True)
    datetimenow = datetime.datetime.now()
    with open('imgs/{}-CH-{}-{}.png'.format(name, self._channel,datetimenow), 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

def main():
    """Main function"""
    cam = HikCamObject('http://192.168.15.42', 80, 'admin', 'Esiexata2017')

    entities = []

    for sensor, channel_list in cam.sensors.items():
        for channel in channel_list:
            entities.append(HikSensor(sensor, channel[1], cam))


main()
