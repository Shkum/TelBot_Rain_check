################################################################################################################


from pyowm import OWM


class Weather:
    owm = OWM('6447d90ffd2f57c8d4fadf48e2127c01')
    exit_thread_flag = False

    def __init__(self, location='Odessa'):
        self.loc = location

    def check_weather(self):
        mgr = self.owm.weather_manager()
        try:
            observation = mgr.weather_at_place(self.loc)
            w = observation.weather
        except:
            w = None
        if w:
            return ['Weather: ' + w.detailed_status, ['Rain: ', w.rain]]  # remove for rain only informing  TEST MESSAGE

            # if not w.rain.keys:  # informing only in case of rain
            #     return 'Rain: ' + w.rain + '\nWeather: ' + w.detailed_status
        else:
            return 'City not found or connection error...'

    def set_location(self, location):
        self.loc = location

    def get_location(self):
        return self.loc


########################################################################################################################


from time import sleep
import telebot
import threading


def read_file(file_name):
    with open(file_name, 'r') as file:
        return file.read()


bot = telebot.TeleBot(read_file('token.ini'))

weather = Weather()

command_flag = False

thread_exit_flag = False


# Function handling 'start' command
@bot.message_handler(commands=["start"])
def start(m):
    global command_flag
    bot.send_message(m.chat.id, 'Enter location name to start rain monitoring:')
    command_flag = True


@bot.message_handler(commands=["stop"])
def stop(m):
    global thread_exit_flag
    bot.send_message(m.chat.id, 'Rain monitoring stopped')
    thread_exit_flag = True


# Getting message from user
@bot.message_handler(content_types=["text"])
def handle_text(message):
    global command_flag
    msg = message.text
    if command_flag:
        weather.set_location(msg)

        wtr = weather.check_weather()
        if wtr != 'City not found or connection error...':
            bot.send_message(message.chat.id, 'New location is: ' + msg)
            bot.send_message(message.chat.id, wtr[0])
            bot.send_message(message.chat.id, 'Rain: ' + str(wtr[1][1]))
            command_flag = False
            while not thread_exit_flag:
                loop_weather_check(message.chat.id)

        else:
            bot.send_message(message.chat.id, 'City not found or connection error...')
            command_flag = False
    else:
        bot.send_message(message.chat.id, 'Your message is: ' + msg)


# loop function, which checking weather and report to telegram in case of rain
def loop_weather_check(chat_id):
    global thread_exit_flag
    while not thread_exit_flag:
        weather_loop = weather.check_weather()
        if weather_loop[1][1].keys():
            bot.send_message(chat_id, 'Rain: ' + str(*weather_loop[1][1].keys()))
            bot.send_message(chat_id, 'Monitoring stopped. Restart it if necessary.')
            thread_exit_flag = True
        sleep(3)
    thread_exit_flag = False
    bot.send_message(chat_id, 'Exit monitoring...')


# start bot
bot.polling(none_stop=True, interval=0)
