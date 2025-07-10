import datetime
import time
import os
import yagmail
from picamera2 import Picamera2
from config import EMAIL_USER, EMAIL_PASS, EMAIL_TO, IMAGE_FOLDER

mailer = yagmail.SMTP(EMAIL_USER, EMAIL_PASS)
picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())


def capture_image():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = os.path.join(IMAGE_FOLDER, f"motion_{timestamp}.jpg")
    picam2.start()
    time.sleep(1)
    picam2.capture_file(image_path)
    picam2.stop()
    return image_path


def send_alert_email(image_path):
    subject = f"[ALERT] Motion detected: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    mailer.send(to=EMAIL_TO, subject=subject, contents=["Motion detected!", image_path])


def cleanup():
    picam2.close()