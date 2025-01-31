IF EXIST app_dist (
    rmdir /s /q app_dist
)

python C:\Users\IDM252577\AppData\Roaming\Python\Python311\Scripts\pyarmor.exe gen -O app_dist -r app

REM Copy logging.yml to app_dist
copy app\logging.yml app_dist\app\logging.yml

REM Create __main__.py to run launch_application
echo from app.app import launch_application > app_dist/__main__.py
echo launch_application() >> app_dist/__main__.py