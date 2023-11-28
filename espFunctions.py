import board
import busio
from digitalio import DigitalInOut
import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi

#A class for handling the esp32 and specific function for connecting to thinkSpeak
class ESP_Tools():
    def __init__(self, ssid_input, pwd_input):
        self._ssid = ssid_input
        self._pwd = pwd_input
        self.esp = None
        self.spi = None
        self.setup()


    #Connects to wifi and sets up the board
    def setup(self):

        esp32_cs = DigitalInOut(board.D13)
        esp32_ready = DigitalInOut(board.D11)
        esp32_reset = DigitalInOut(board.D12)

        self.spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
        self.esp = adafruit_esp32spi.ESP_SPIcontrol(self.spi, esp32_cs, esp32_ready, esp32_reset)

        requests.set_socket(socket, self.esp)

        if self.esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
            print("ESP32 found and in idle mode")

        num_trys = 0
        max_num_trys = 5
        print("Connecting to network")
        while not self.esp.is_connected:
            num_trys += 1
            if( num_trys >= max_num_trys):
                print("Unable to connect to wifi: Timeout error")
                raise TimeoutError("Unable to connect to wifi: Timeout error")
            try:
                self.esp.connect_AP(self._ssid, self._pwd)
            except RuntimeError as e:
                print("could not connect to AP, retrying: ", e)
                continue
        print("Connected to", str(self.esp.ssid, "utf-8"), "\tRSSI:", self.esp.rssi)
        print("My IP address is", self.esp.pretty_ip(self.esp.ip_address))

    def restart(self):
        print("Reseting the socket")
        requests.set_socket(socket, self.esp)

        if self.esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
            print("ESP32 found and in idle mode")

        num_trys = 0
        max_num_trys = 5
        print("Connecting to network")
        while not self.esp.is_connected:
            num_trys += 1
            if( num_trys >= max_num_trys):
                print("Unable to connect to wifi: Timeout error")
                raise TimeoutError("Unable to connect to wifi: Timeout error")
            try:
                self.esp.connect_AP(self._ssid, self._pwd)
            except RuntimeError as e:
                print("could not connect to AP, retrying: ", e)
                continue
        print("Connected to", str(self.esp.ssid, "utf-8"), "\tRSSI:", self.esp.rssi)
        print("My IP address is", self.esp.pretty_ip(self.esp.ip_address))
    #Pushes data to a specified field

    def api_get(self, request):
        request_msg = request
        print(request_msg)
        try:
            r = requests.get(request_msg)
            response = r.text
            r.close()
        except RuntimeError as e:
            print("could not complete request error: ", e)
            return e
        return response

    def api_post(self, request, data=None, json=None):
        request_msg = request
        if(data is not None):
            data = data.encode('utf-8')
        if(json is not None):
            json = json.encode('utf-8')
        print(request_msg)
        try:
            r = requests.request('POST', request, data=data, json=json)
        except RuntimeError as e:
            print("could not complete request error: ", e)
            return e
