from io import BytesIO
from urllib import response
import requests
from PIL import Image
from requests.exceptions import ConnectionError
class JarvisCamera:
    def __init__(self, ip: str, photo_dir: str, camera_name: str):
        self.camera_name = camera_name
        self.camera_address = f"http://{ip}"
        self.photo_dir = photo_dir
        self.CAMERA_DEFAULTS = [
            "framesize&val=8",
            "quality&val=10",
            "awb&val=1",
            "awb_gain&val=1",
            "wb_mode&val=0",
            "aec&val=1",
            "aec2&val=1",
            "ae_level&val=2",
            "gainceiling&val=6",
            "bpc&val=1",
            "wpc&val=1",
            "raw_gma&val=1",
            "lenc&val=1",
            "hmirror&val=1",
            "vflip&val=1",
        ]
        self.set_defaults()
        self.photo_count = 0

    def set_defaults(self):
        errors = 0
        for camera_default in self.CAMERA_DEFAULTS :
            try:
                url = f"{self.camera_address}/control?var={camera_default}"
                r = requests.get(url, verify=False, timeout=1)
                if r.status_code != 200:
                    errors = errors + 1
                    break
            except ConnectionError:
                print("Camera Failed to connect")
            except requests.ReadTimeout:
                print("Camera timed out")

    def get_photo(self):
        file_path = None
        try:
            snapshot = requests.get(f'{self.camera_address}/capture?', verify=False, timeout=1)
            file_path = f"{self.photo_dir}snapshot.jpg"
            with open(file_path,'wb') as f:
                f.write(snapshot.content)
        except ConnectionError:
            print("Camera timed out")
        except requests.ReadTimeout:
            print("Camera timed out")
        except IOError:
            print("File saving error when creating photo")
        self.photo_count = self.photo_count
        return file_path

    def get_photo_bw(self):
        im = None
        try:
            response = requests.get(f'{self.camera_address}/capture?', verify=False, timeout=1)
            image_data = Image.open(BytesIO(response.content))
            im  = self.format_photo(image_data, optimum_size=(400,240))
        except ConnectionError:
            pass
        except requests.ReadTimeout:
            pass
        return im

    def format_photo(self, im, optimum_size):
        try:
            preferred_width,preferred_height = optimum_size
            im.thumbnail((preferred_width, 400))
            actual_width, actual_height = im.size
            height_remainder = actual_height - preferred_height
            top = height_remainder / 2
            bottom = actual_height - (height_remainder / 2)
            im = im.crop((0, top, preferred_width, bottom))
            im = im.convert('1')
        except AttributeError:
            print("Pillow failed to open the original image")
        except IOError:
            print("File saving error when creating thumbnail")
        return im

def main():
    import os
    photo_dir = f"{os.getcwd()}/photos"
    door_camera = JarvisCamera(
        ip = "192.168.0.62", 
        photo_dir = photo_dir, 
        camera_name = "door cam"
    )


if __name__ == "__main__":
    main()