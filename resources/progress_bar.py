token = '5315086487:AAHfIZxWoBlgI2k9MkQ0UshYVx_p7m3GNyA'
chat_id = "2121319133"
import time

from tqdm.contrib.telegram import trange
for i in trange(100, token=token, chat_id=chat_id):
    time.sleep(0.1)
    print(i)

