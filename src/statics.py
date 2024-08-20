import os
from functions import *

UPLOAD_PATH = None
DOWNLOAD_PATH = None

uploads = 'assets/uploads'
downloads = 'assets/downloads'
files = [f for f in os.listdir(uploads) if os.path.isfile(os.path.join(uploads, f))]
