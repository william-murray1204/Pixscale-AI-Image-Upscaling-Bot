# Pixscale_Telegram_Bot


## Installation
1. Clone repo
    git clone https://github.com/william-murray1204/Pixscale_Telegram.git
    cd Pixscale_Telegram

2. Install dependent packages
    pip install -r requirements.txt

3. Create .env file with the following
    SERVER_IP =
    DATABASE_PORT =
    DATABASE_USER =
    DATABASE_PASSWORD =
    DATABASE_NAME =
    POOL_NAME =
    POOL_SIZE =
    PIXSCALE_API_KEY =
    EDWIN_API_KEY =
    ADMIN_CHATID =
    STRIPE_PROVIDER_TOKEN =

4. Build Dockerfile
    docker build .




## To do
- Stop the algorithm from running tiling twice
- Get Docker working
- Setup real payment system
- Fix payments for pixscale
- Add a warning message when the bot is being used to say we are under strain and a link to donate to show how (if you like what we do, any donations small or large help us continuall improve our services helping us to deliver you a better user experience. Thanks for your understanding.)
- Advertise on r/dropshipping
- Create desktop application and allow local calculation or cloud callculation and pixscale access from within file explorer (Software license)
- ^^^ will have to update license in model files from original esrgan for mit license etc

[https://medium.com/codex/how-im-making-over-400-per-month-with-a-simple-bot-2c78afba4d54](https://medium.com/codex/how-im-making-over-400-per-month-with-a-simple-bot-2c78afba4d54)


## Connecting a Stripe Token
Use the /mybots command in the chat with BotFather and choose the @merchantbot that will be offering goods or services.
Go to Bot Settings > Payments.
Choose a provider, and you will be redirected to the relevant bot.
Enter the required details so that the payments provider is connected successfully, go back to the chat with Botfather.
The message will now show available providers. Each will have a name, a token, and the date the provider was connected.
You will use the token when working with the Bot API.