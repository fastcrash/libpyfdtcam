import requests

class FDTCam(object):
    def __init__(self, host, port, user, password):
        self._host = host
        self._user = user
        self._password = password
        self._port = port
        self.session = requests.Session()



    @property
    def __baseurl(self):
        """Base URL used CGI API requests on FDT Camera."""
        return "http://" + self._host + \
               "/cgi-bin/hi3510/param.cgi?cmd={}&-usr=" + \
               self._user + "&-pwd=" + self._password

    @property
    def __command_url(self):
        """Base command URL used by CGI API requests."""
        return "http://" + self._host + \
               "/cgi-bin/hi3510/{}&-usr=" + \
               self._user + "&-pwd=" + self._password

    def query(self, cmd, raw=False):
        """Generic abstraction to run query."""
        url = self.__baseurl.format(cmd)
        req = self.session.get(url)
        if not req.ok:
            req.raise_for_status()

        return req.text if raw else self.to_dict(req.text)

    def send(self, cmd, payload=None, raw=False):
        url = self.__baseurl.format(cmd)
        for k, v in payload.items():
            url += "&-" + k + "=" + v
        print(url)
        req = self.session.get(url)
        if not req.ok:
            req.raise_for_status()

    @property
    def device_type(self):
        """Return device type."""
        return self.query('getdevtype').get('devtype')


    def get_snapshot(self, filename=None):
        """Return camera snapshot."""
        url = self.__command_url.format('web/tmpfs/auto.jpg')

        req = self.session.get(url)
        if req.ok:
            if filename is None:
                return req.content

            with open(filename, 'wb') as snap:
                snap.write(req.content)
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
        payload = {"infraredstat":status}
        self.send('setinfrared', payload)

    @property
    def ptz_preset(self):
        return

    @ptz_preset.setter
    def ptz_preset(self, preset):
        preset -= 1
        preset = str(preset)
        payload = {"act": "goto", "number": preset}
        self.send('preset', payload)

    def ptz_control(self, act, speed, step=1):
        payload = {"act": act, "speed": str(speed), "step": str(step)}
        self.send('ptzctrl', payload)

    def ptz_up(self):
        self.ptz_control("up", 45, 0)

    def ptz_down(self):
        self.ptz_control("down", 45, 0)

    def ptz_left(self):
        self.ptz_control("left", 45, 0)

    def ptz_right(self):
        self.ptz_control("right", 45, 0)

    def ptz_stop(self):
        self.ptz_control("stop", 45, 0)

    @property
    def motion_detect(self):
        return bool(self.query("getmdattr").get("m1_enable"))

    @motion_detect.setter
    def motion_detect(self, status, area=1, sens=50):
        payload = {"enable": str(status), "area": str(area), "s": str(sens)}
        self.send("setmdattr", payload)

    def motion_on(self):
        self.motion_detect(1)

    def motion_off(self):
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
