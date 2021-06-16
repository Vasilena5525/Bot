from coinbase.wallet.client import Client
from telegram import ParseMode, Update
from telegram.ext import CommandHandler, Defaults, Updater, CallbackContext

COINBASE_KEY = 'Hq8S8dSFgpHb4Oe4'
COINBASE_SECRET = 'R3Dp2nwgbvQ4ArOmvhKewYDEgHHnpcm2' 
TELEGRAM_TOKEN = '1890711761:AAHVrKm1rq5ZpfRUvbYcBh0E_tj6NYJI4UU'

coinbase_client = Client(COINBASE_KEY, COINBASE_SECRET)


#PRICE ALERT
def startCommand(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=(f'Hello {update.effective_user.first_name}' + "👋"  + '\nMy job is to notify you whenever your crypto currency of interest changes its price trend. 📈📉'))

def priceAlert(update, context):
    if len(context.args) > 2:
        crypto = context.args[0].upper()
        sign = context.args[1]
        price = context.args[2]

        context.job_queue.run_repeating(priceAlertCallback, interval=15, first=15, context=[crypto, sign, price, update.message.chat_id])
        
        response = f"⏳ I will send you a message when the price of {crypto} reaches £{price}, \n"
        response += f"the current price of {crypto} is £{coinbase_client.get_spot_price(currency_pair=crypto + '-GBP')['amount']}"
    else:
        response = '⚠️ Please provide a crypto code and a price value following this example: \n<i>/alert {crypto code} {> / &lt;} {price}</i>'
    
    context.bot.send_message(chat_id=update.effective_chat.id, text=response)

def priceAlertCallback(context):
    crypto = context.job.context[0]
    sign = context.job.context[1]
    price = context.job.context[2]
    chat_id = context.job.context[3]

    send = False
    spot_price = coinbase_client.get_spot_price(currency_pair=crypto + '-GBP')['amount']

    if sign == '<':
        if float(price) >= float(spot_price):
            send = True
    else:
        if float(price) <= float(spot_price):
            send = True

    if send:
        response = f'👋 Hey, {crypto} has surpassed £{price} and has just reached <b>£{spot_price}</b>!'

        context.job.schedule_removal()

        context.bot.send_message(chat_id=chat_id, text=response)

if __name__ == '__main__':
    updater = Updater(token=TELEGRAM_TOKEN, defaults=Defaults(parse_mode=ParseMode.HTML))
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler("start", startCommand)) # Accessed via /start
    dispatcher.add_handler(CommandHandler("alert", priceAlert)) # Accessed via /alert

    updater.start_polling() # Start the bot

    updater.idle() # Wait for the script to be stopped, this will stop the bot as well        