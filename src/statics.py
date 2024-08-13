import os
import flet as ft
from functions import *

uploads = 'assets/uploads'
downloads = 'assets/downloads'
files = [f for f in os.listdir(uploads) if os.path.isfile(os.path.join(uploads, f))]
