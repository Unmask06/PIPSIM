IF EXIST pipesim-pilot (
    rmdir /s /q pipesim-pilot
)

python C:\Users\IDM252577\AppData\Roaming\Python\Python311\Scripts\pyarmor.exe gen -O pipesim-pilot -r app

REM Copy logging.yml to app_dist
copy app\logging.yml pipesim-pilot\app\logging.yml

REM Create __main__.py to run launch_application
echo from app.app import launch_application > pipesim-pilot/__main__.py
echo launch_application() >> pipesim-pilot/__main__.py