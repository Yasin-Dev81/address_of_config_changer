import telebot
from telebot import types
import requests


class CFIPs:
    def __init__(self) -> None:
        self.ips = {}
        self.yasin_ips = []
        self.raw_data = None
        self.operators = {
            'MCI': 'Hamrah Aval',
            'RTL': 'Rightel',
            'AST': 'Asiatek',
            'IRC': 'Irancel',
            'SHT': 'Shatel',
            'MKB': 'Mokhaberat',
            'MBT': 'Mobinnet',
            'ZTL': 'Zitel',
            'PRS': 'ParsOnline',
            'HWB': 'Hiweb',
        }

    def get_ip_from_sudoer(self):
        r = requests.get('http://bot.sudoer.net/best.cf.iran')
        if r.status_code == 200:
            self.raw_data = r.text
            return True
        else:
            return False

    def arange_ips(self):
        if self.get_ip_from_sudoer():
            separated_by_operator = self.raw_data.split('\n')
            separated_by_operator.pop()
            for i in separated_by_operator:
                if 'IRC' in i:
                    operator = i.split()
                else:
                    operator = (i.split(' \t ')[0]).split()
                self.ips[operator[0]] = operator[1]
            return True
        else:
            raise Exception('Error in get of sudoer')
    
    def get_ip_dic(self):
        if self.arange_ips():
            return self.ips
        else:
            raise Exception('Not arranged')

    def get_yasin_ips(self):
        with open('yasin_ips.txt', 'r') as f:
            self.yasin_ips = (f.read()).split('\n')
            while '' in self.yasin_ips:
                self.yasin_ips.remove('')
        return True


class ChangeAddress(CFIPs):
    def __init__(self, config: str) -> None:
        super().__init__()
        self.arange_ips()
        self.raw_config = config
        self.base_vless = []
        self.output_configs = []

    def convert_raw_config_to_base(self):
        splited_raw_config = self.raw_config.split('@')
        self.base_vless.append(
            splited_raw_config[0] + '@'
        )
        self.base_vless.append(
            '?' + (splited_raw_config[1].split('?')[-1])
        )
        return True
    
    def change_address_with_choose_operator(self, operator: str):
        if operator in self.ips.keys() and self.convert_raw_config_to_base():
            self.output_configs.append(
                self.base_vless[0]+self.ips.get(operator)+self.base_vless[1]+'[%s]'%self.ips.get(operator)
            )
        else:
            raise Exception('There is no operator')

    def change_address_with_all_operator(self):
        if self.convert_raw_config_to_base():
            for operator in self.ips:
                self.output_configs.append(
                    self.base_vless[0]+self.ips.get(operator)+self.base_vless[1]+'[%s]'%self.ips.get(operator)
                )
                # print(
                #     self.base_vless[0],
                #     self.ips.get(operator),
                #     self.base_vless[1],
                #     sep=''
                # )
            return self.output_configs

    def change_address_with_yasin_ips(self):
        if self.get_yasin_ips() and self.convert_raw_config_to_base():
            for ip in self.yasin_ips:
                self.output_configs.append(
                    self.base_vless[0]+ip+self.base_vless[1]+'[%s]'%ip
                )
                # print(
                #     self.base_vless[0],
                #     self.ips.get(operator),
                #     self.base_vless[1],
                #     sep=''
                # )
            return self.output_configs



bot = telebot.TeleBot("5816813852:AAEr15BSg3_zFUpNcw2t3Cmx8FYkbqWXGm4")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # print(message)
    bot.reply_to(
        message=message, 
        text=(
            'سلام\n'
            'این ربات آدرس کانفیگ‌های v2ray رو به آی‌پی‌های سالم و فیلتر نشده کلودفلری که ربات sudoer شناسایی کرده تغییر میده:)\n'
            'فقظ کافیه کانفیگ خودتون رو ارسال کنید\n'
            '‼️ ربات فعلا فقط از کانفیگ‌های با پورتکل vless پشتیبانی میکنه!\n'
        ),
        parse_mode='HTML'
    )


@bot.message_handler(func=lambda message: ('vless' in message.text) and (message.text.count('vless') == 1))
def change_vless(message):
    cl = CFIPs()

    operators_markup = types.InlineKeyboardMarkup(row_width=1)
    for operator in cl.operators:
        operators_markup.add(
            types.InlineKeyboardButton(
                text=cl.operators.get(operator),
                callback_data=operator,
            )
        )
    else:
        operators_markup.add(
            types.InlineKeyboardButton(
                text='All',
                callback_data='all'
            )
        )
        operators_markup.add(
            types.InlineKeyboardButton(
                text='Suggested by Yasin',
                callback_data='yasin'
            )
        )
        operators_markup.add(
            types.InlineKeyboardButton(
                text='Suggested by Yasin+All',
                callback_data='yasin_all'
            )
        )

    bot.reply_to(
        message=message, 
        text=(
            'all: همه‌ی اوپراتورها\n'
            'Suggested by Yasin: آی‌پی‌های پیشنهادی من\n'
            'دیدن آی‌پی‌ها: http://bot.sudoer.net/best.cf.iran'
        ),
        reply_markup=operators_markup
    )

    bot.send_message(
        chat_id='-1001474981907',
        text="<code>%s</code>" % message.text,
        parse_mode='HTML'
    )


@bot.message_handler(func=lambda message: ('vless' in message.text) and (message.text.count('vless') == 0))
def send_error(message):
    bot.reply_to(
        message=message,
        text="لطفا یه کانفیگ با پورتکل vless ارسال کنید!"
    )


@bot.message_handler(func=lambda message: ('vless' in message.text) and (message.text.count('vless') > 1))
def send_error(message):
    bot.reply_to(
        message=message,
        text="لطفا در هر پیام فقط یه کانفیگ ارسال کنید\nبا تشکر"
    )


@bot.callback_query_handler(func=lambda call: True)
def change_vless_called(call): 
    cl = ChangeAddress(
        config=(call.message.json).get('reply_to_message').get('text')
    )

    if call.data == 'all':
        cl.change_address_with_all_operator()
    elif call.data == 'yasin':
        cl.change_address_with_yasin_ips()
    elif call.data == 'yasin_all':
        cl.change_address_with_all_operator()
        cl.change_address_with_yasin_ips()
    else:
        cl.change_address_with_choose_operator(call.data)

    config_message = ''
    for conf in cl.output_configs: config_message += conf + '\n'

    bot.reply_to(
        message=call.message,
        text="<code>%s</code>" % config_message,
        parse_mode='HTML'
    )
    bot.send_message(
        chat_id=(call.message.json).get('chat').get('id'),
        text="<i>Powered by</i> <b>{admin}</b>".format(admin='@yasindev81'),
        parse_mode='html',
    )


bot.infinity_polling()
