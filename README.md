# Pixscale_Telegram_Bot


## Installation
1. Clone repo

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


## Connecting a Stripe Token
Use the /mybots command in the chat with BotFather and choose the @merchantbot that will be offering goods or services.
Go to Bot Settings > Payments.
Choose a provider, and you will be redirected to the relevant bot.
Enter the required details so that the payments provider is connected successfully, go back to the chat with Botfather.
The message will now show available providers. Each will have a name, a token, and the date the provider was connected.
You will use the token when working with the Bot API.
