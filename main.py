
from Ranking import ranking


import telebot


bot = telebot.TeleBot('6575723552:AAE0FExVL55M6iZeo1MN-IJOA1OljvZUPOE')

import os

from news_regressor.news_regressor import NewsRegressor
from upload import upload_data_from_moexalgo, read_data_stock
from datetime import datetime, timedelta
from telebot import types
from agent import predict, get_ticket_price, get_TP_SL


if __name__ == '__main__':
    # os.system("pip3 install --upgrade pip'")
    # os.system("pip3 install 'etna[torch]'")
    # os.system("pip3 install 'etna[auto]'")
    # os.system("pip3 install 'etna[statsforecast]'")
    # os.system("pip3 install 'etna[classification]'")
    # os.system("pip3 install 'etna[prophet]'")
    # os.system("pip3 install 'etna[all]'")

    def get_tiket():
        """Получаем тикеты для фокусирования бота"""
        listing = read_data_stock()
        tikets = listing[(listing['INSTRUMENT_TYPE'] == 'Акция обыкновенная') |
                         (listing['INSTRUMENT_TYPE'] == 'Акции иностранного эмитента')]['TRADE_CODE'].unique()
        print(f"Ранжируем {len(tikets)} акций")
        ranking_listing, metrics = ranking(tikets)

        return ' '.join(ranking_listing[:5]), metrics

    ranked_tiket, metrics = get_tiket()

    df = read_data_stock()
    list_tradecode = df['TRADE_CODE'].unique().tolist()

    ticket_lists = [str(i).lower() for i in list_tradecode]
    NR = NewsRegressor()


    @bot.message_handler(commands=['start'])
    def start(message):

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("👋 Поздороваться")
        markup.add(btn1)
        bot.send_message(message.from_user.id, "👋 Привет! Я - твой бот-помошник для трейдинга!", reply_markup=markup)


    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Предсказать поведение акции')
        btn2 = types.KeyboardButton('Оценить влияние новости')
        btn3 = types.KeyboardButton('Выбрать лучшие акции для торговли')
        markup.add(btn1, btn2, btn3)
        if message.text == '👋 Поздороваться':

            bot.send_message(message.from_user.id, 'Какой функционал тебя интересует?',
                             reply_markup=markup)  # ответ бота

        elif message.text == 'Предсказать поведение акции':
            bot.send_message(message.from_user.id, 'Напиши мне тикет акции, а я верну предсказание')

        elif message.text == 'Оценить влияние новости':
            bot.send_message(message.from_user.id, 'Отправь мне новость')

        elif message.text == 'Выбрать лучшие акции для торговли':
            bot.send_message(message.from_user.id, f'Лучшие акции для торговли сейчас: {str(ranked_tiket)} \n метрики этих акций : {metrics}',
                             reply_markup=markup)

        elif str(message.text).strip().lower() in ticket_lists:
            ticket = str(message.text).strip().upper()

            date_now = datetime.today().date()
            last_date = datetime.today() - timedelta(days=180)

            horizon = 60

            bot.send_message(message.from_user.id, "Гружу данные из moexalgo")
            tradestats, orderstats, obstats = upload_data_from_moexalgo(ticket, last_date.date(), date_now)

            bot.send_message(message.from_user.id, "Считаю цену в будущем...")

            inside = predict(tradestats, orderstats, obstats, horizon)

            df_price = inside[inside["segment"] == "price"].reset_index(drop=True)

            last_price, date_time = get_ticket_price(ticket, df_price, horizon)

            bot.send_message(message.from_user.id, "Считаю Take profit и Stop loss...")

            take_profit, stop_loss = get_TP_SL(inside, last_price, horizon)

            bot.send_message(message.from_user.id,
                             f'Акция {ticket} \n Цена покупки: {last_price} \n Take profit нужно поставить на: {take_profit}\n Stop loss нужно поставить на: {stop_loss}')

        else:
            bot.send_message(message.from_user.id, "Кажется ты мне отправил новость, я сейчас оценю ее влияния")

            text = message.text

            text_predictor = NR.predict_news(text)

            if text_predictor > 0:
                bot.send_message(message.from_user.id,
                                 f'Данная новость может повлиять положительно на цену акции на {text_predictor}%')
            else:
                bot.send_message(message.from_user.id,
                                 f'Данная новость может повлиять отрицательно на цену акции на {text_predictor}%')


    bot.infinity_polling(timeout=10, long_polling_timeout=5)
