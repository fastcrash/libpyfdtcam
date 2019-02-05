""""
A small Library for FDT IP-Cams.
"""

import requests

class FDTCam(object):
    def __init__(self, host, port, username, password):
        self._host = host
        self._username = username
        self._password = password
        self._port = port
        self.session = requests.Session()



    @property
    def __baseurl(self):
        """Base URL used CGI API requests on FDT Camera."""
        return "http://" + self._host + \
               "/cgi-bin/hi3510/param.cgi?cmd={}&-usr=" + \
               self._username + "&-pwd=" + self._password

    @property
    def __command_url(self):
        """Base command URL used by CGI API requests."""
        return "http://" + self._host + \
               "/cgi-bin/hi3510/{}&-usr=" + \
               self._username + "&-pwd=" + self._password

    def query(self, cmd, raw=False):
        """Generic abstraction to run query."""
        url = self.__baseurl.format(cmd)
        req = self.session.get(url)
        if not req.ok:
            req.raise_for_status()

        return req.text if raw else self.to_dict(req.text)

    def send(self, cmd, payload=None, raw=False, callback=False):
        """Sends Command via CGI. Payload has to be dictionary with 'parameter:value' format."""
        # Build URL for command.
        url = self.__baseurl.format(cmd)
        # Add payload to url.
        for k, v in payload.items():
            url += "&-" + k + "=" + v

        req = self.session.get(url)

        if not req.ok:
            req.raise_for_status()

        if callback:
            return req.text if raw else self.to_dict(req.text)

    @property
    def device_type(self):
        """Return device type."""
        return self.query('getdevtype').get('devtype')


    def get_snapshot(self):
        """Return camera snapshot."""
        url = self.__command_url.format('web/tmpfs/auto.jpg')

        req = self.session.get(url)
        if req.ok:
            return req.content

        return req

    @property
    def factory_reset(self):
        """Restore factory settings."""
        url = self.__command_url.format('sysreset.cgi')
        return self.session.get(url)

    @property
    def reboot(self):
        """Reboot camera."""
        url = self.__command_url.format('sysreboot.cgi')
        return self.session.get(url)

    @property
    def ir_status(self):
        """ Status of IR-LED """
        return bool(self.query('getinfrared').get('infraredstat'))

    @ir_status.setter
    def ir_status(self, status):
        """ Set status of IR-LED """
        payload = {"infraredstat":status}
        self.send('setinfrared', payload)

    def ir_on(self):
        self.send("setinfrared", 1)
        """ Switch IR-LED on """

    def ir_off(self):
        """ Switch IR-LED off """
        self.send("setinfrared", 0)

    
    def ptz_preset(self, preset):
        """ Move cam to PTZ preset."""
        preset -= 1
        preset = str(preset)
        payload = {"act": "goto", "number": preset}
        self.send('preset', payload)

    def ptz_control(self, act, speed, step=1):
        """ Send PTZ control command."""
        payload = {"act": act, "speed": str(speed), "step": str(step)}
        self.send('ptzctrl', payload)

    def ptz_up(self):
        """ Move cam up. """
        self.ptz_control("up", 45, 0)

    def ptz_down(self):
        """ Move cam down. """
        self.ptz_control("down", 45, 0)

    def ptz_left(self):
        """ Move cam left. """
        self.ptz_control("left", 45, 0)

    def ptz_right(self):
        """ Move cam right. """
        self.ptz_control("right", 45, 0)

    def ptz_stop(self):
        """ Stop PTZ. """
        self.ptz_control("stop", 45, 0)

    @property
    def motion_detect(self):
        """ Get status of Motion Detection. """
        return bool(self.query("getmdattr").get("m1_enable"))

    @motion_detect.setter
    def motion_detect(self, status, area=1, sens=50):
        """ Set status of Motion Detection """
        payload = {"enable": str(status), "area": str(area), "s": str(sens)}
        self.send("setmdattr", payload)

    def motion_on(self):
        """ Activate Motion Detection. """
        self.motion_detect(1)

    def motion_off(self):
        """ Deactivate Motion Detection. """
        self.motion_detect(0)

    def to_dict(self, response):
        """Format response to dict."""
        # dict to return
        rdict = {}

        # remove single quotes and semi-collon characters
        response = response.replace('\'', '').replace(';', '')

        # eliminate 'var ' from response and create a list
        rlist = [l.split('var ', 1)[1] for l in response.splitlines()]

        # for each member of the list, remove the double quotes
        # and populate dictionary
        for item in rlist:
            key, value = item.replace('"', '').strip().split('=')
            rdict[key] = value

        return rdict
