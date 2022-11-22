# Pixscale_Telegram_Bot

# Pip Installs
pip install python-dotenv
pip install pyTelegramBotAPI
pip install mysql-connector-python
pip install opencv-python
pip install requests
pip install Pillow
pip install ffmpeg-python
pip install gfpgan
pip install tqdm
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu117
pip install basicsr


# Model Download Path
wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth -P weights
wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth -P weights
wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth -P weights
wget https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth





# Environment File Requirements
SERVER_IP=''
DATABASE_PORT=
DATABASE_USER=''
DATABASE_PASSWORD=''
DATABASE_NAME=''
POOL_NAME=''
POOL_SIZE=


PIXSCALE_API_KEY = ''
EDWIN_API_KEY = ''
ADMIN_CHATID = ''



### To do

- Real payment system

[https://medium.com/codex/how-im-making-over-400-per-month-with-a-simple-bot-2c78afba4d54](https://medium.com/codex/how-im-making-over-400-per-month-with-a-simple-bot-2c78afba4d54)