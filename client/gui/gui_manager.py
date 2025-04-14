from customtkinter import *
from json import load
import asyncio
import threading
import time
from functools import partial

from communicate.client import client
from communicate.service import *
from tkintermapview import TkinterMapView


class GUIManager:
    def __init__(self):
        self.app = CTk()
        self.app.title("ShadyPay Банкинг")
        self.width = 500
        self.height = 700
        self.app.geometry(f"{self.width}x{self.height}")

        self.config = {}
        with open("data/client_config.json", "r", encoding="UTF-8") as json_file:
            self.config = load(json_file)

        self.font = self.config['font']
        for i in self.font:
            self.font[i] = tuple(self.font[i])

        self.user_data = {}

    async def wait_connection(self, n=0):
        try:
            bool_check = check_auth()
            return bool_check
        except:
            if n > 3:
                return "offline"
            await asyncio.sleep(1)
            return await self.wait_connection(n+1)

    async def asynsleep(self):
        await asyncio.sleep(3)

    def main(self):
        def check_connection_thread():
            try:
                bool_check = check_auth()
            except Exception as e:
                self.open_popup(e)
                bool_check = asyncio.run(self.wait_connection())

            if bool_check == "offline":
                self.app.after(0, self.open_popup, "Нет подключения к серверу, попробуйте позже")
                asyncio.run(self.asynsleep())
                self.app.quit()
            if bool_check:
                self.app.after(0, self.authorizate_buid)
            else:
                self.app.after(0, self.non_authorizate_buid)

        connection_thread = threading.Thread(target=check_connection_thread, daemon=True)
        connection_thread.start()

        self.app.mainloop()

    def update_user_data(self):
        try:
            self.user_data = get_user_data()
            print("Получены данные пользователя:", self.user_data)  # Отладочная информация
        except Exception as e:
            raise e
            print("Ошибка при получении данных:", str(e))  # Отладочная информация
            self.open_popup(e)

    def authorizate_buid(self):
        def run():
            try:
                self.update_user_data()
                print("Данные перед построением интерфейса:", self.user_data)  # Отладочная информация
                self.app.after(0, self._build_authorized_interface)
            except Exception as e:
                raise e
                print("Ошибка в потоке авторизации:", str(e))  # Отладочная информация
                self.app.after(0, self.open_popup, str(e))

        threading.Thread(target=run, daemon=True).start()

    def _build_authorized_interface(self):

        self.tabview = CTkTabview(self.app, anchor="s")
        self.tabview.pack(expand=True, fill='both')

        self.payment_tab = self.tabview.add("Платежи")
        self.main_tab = self.tabview.add("Главная")
        self.personal_account = self.tabview.add("Кабинет")

        self.build_payment_tab()
        self.build_main_tab()
        self.build_personal_account()


    def build_payment_tab(self):
        #TODO: построить вкладку платежей
        pass

    def fin_proccesing(self, product_type, is_named_product, currency, is_agree1, is_agree2):
        if not (is_agree1.get() and is_agree2.get()):
            self.open_popup("Вы должны согласиться с \nполитикой конфиденциальности и пользования")
            return

        try:
            product_type = product_type.get()
            is_named_product = is_named_product.get()
            currency = currency.get()

            if not product_type or not currency:
                raise ValueError("Выберите тип продукта и валюту")

            create_product(product_type, is_named_product, currency)
        except Exception as e:
            self.open_popup(e)
            return

        self.fin_wind.destroy()

    def show_create_fin_window(self):
        def update_currency(product_tupe, currency, description):
            if product_tupe == "Криптокарта":
                currency.configure(values=["SHD"])
                currency.set("SHD")
            else:
                currency.configure(values=["BYN", "USD", "EUR", "RUB"])
                currency.set("BYN")
            description.configure(text=self.config['descriptions'][product_tupe])

        self.fin_wind = CTkToplevel(self.app)
        self.fin_wind.title("Новый продукт")
        main_x = self.app.winfo_x()
        main_y = self.app.winfo_y()
        self.fin_wind.geometry(f"{self.width - 10}x{self.height - 10}+{main_x+5}+{main_y + 5}")

        CTkLabel(self.fin_wind, text="Создай новый продукт", font=self.font["h4"]).pack(pady=10)

        currency = CTkComboBox(self.fin_wind,
                               values=["BYN", "USD", "EUR", "RUB"],
                               command=print,
                               width=200)
        description = CTkLabel(self.fin_wind,
                               text=self.config['descriptions']["Дебетовая карта"],
                               justify="left", font=self.font['p'])

        CTkLabel(self.fin_wind, text="Тип продукта", font=self.font['h5']).place(x=self.width*0.15, y=40)
        product_type = CTkComboBox(self.fin_wind,
                            values=["Дебетовая карта", "Кредитная карта", "Овердрафтная карта", "Кредит", "Копилка", "Криптокарта"],
                            command= lambda value: update_currency(value, currency, description),
                            width=200)
        product_type.place(x=self.width*0.35, y=40)

        CTkLabel(self.fin_wind, text="Имя на карте:", font=self.font['h5']).place(x=self.width*0.15, y=80)
        is_named_product = CTkCheckBox(self.fin_wind, text="", font=self.font['h5'])
        is_named_product.place(x=self.width*0.35, y=80)
        is_named_product.select()

        CTkLabel(self.fin_wind, text="Валюта:", font=self.font['h5']).place(x=self.width*0.15, y=120)

        currency.place(x=self.width*0.35, y=120)

        description.place(x=self.width*0.15, y=200)


        CTkLabel(self.fin_wind, text="Я ознакомлен с политикой конфеденциальности", font=self.font['litp']).place(x=self.width*0.25, y=560)
        is_agree1 = CTkCheckBox(self.fin_wind, text="", font=self.font['h5'])
        is_agree1.place(x=self.width*0.75, y=560)
        CTkLabel(self.fin_wind, text="Я согласен с политикой пользования", font=self.font['litp']).place(x=self.width*0.25, y=590)
        is_agree2 = CTkCheckBox(self.fin_wind, text="", font=self.font['h5'])
        is_agree2.place(x=self.width*0.75, y=590)
        CTkButton(self.fin_wind,
                  command=lambda : self.fin_proccesing(product_type, is_named_product, currency, is_agree1, is_agree2),
                  text="Создать"
                  ).place(x=self.width*0.35, y=630)

        # Модальное поведение (блокирует фон до закрытия)
        self.fin_wind.grab_set()

    def on_card_click(self, card):
        def change_label(label, text):
            self.adr_entry.destroy()
            if text == "Телефону":
                self.adr_entry = CTkEntry(self.card_wind)
                label.configure(text="Номер Телефона:")
            elif text == "Номеру карты":
                self.adr_entry = CTkEntry(self.card_wind)
                label.configure(text="Номер карты:")
            elif text == "На свой счет":
                self.adr_entry = CTkComboBox(self.card_wind,
                                        values=[card['card_number'] for card in self.user_data['cards']],
                                        command=print,
                                        width=200)
                label.configure(text="Выберите карту:")
            self.adr_entry.place(x=self.width * 0.45, y=335)

        def transfer(card_number, adr, sum, transfer_type):
            try:
                if not adr or not sum:
                    raise ValueError("Заполните все поля")
                if transfer_type == "Телефону" and len(adr) != 13:
                    raise ValueError("Неверный номер телефона")
                if transfer_type == "Номеру карты" and len(adr) != 16:
                    raise ValueError("Неверный номер карты")
                answer = transfer_service(card_number, adr, sum, transfer_type)
                self.open_popup(answer, "Уведомление")
                self.card_wind.destroy()
            except Exception as e:
                raise e
                self.open_popup(e)

        def delete_card(card_number):
            print("ПУПУРУПУПУ,ТАТАРАТАТА")

        self.card_wind = CTkToplevel(self.app)
        self.card_wind.title("Информация о карте")
        main_x = self.app.winfo_x()
        main_y = self.app.winfo_y()
        self.card_wind.geometry(f"{self.width - 10}x{self.height - 10}+{main_x + 5}+{main_y + 5}")
        CTkLabel(self.card_wind, text="Информация о карте", font=self.font["h4"]).pack(pady=10)
        CTkLabel(self.card_wind, text="Тип карты:", font=self.font['h5']).place(x=self.width * 0.15, y=50)
        CTkLabel(self.card_wind, text=card['type'], font=self.font['h5']).place(x=self.width * 0.35, y=50)
        CTkLabel(self.card_wind, text="Валюта:", font=self.font['h5']).place(x=self.width * 0.15, y=70)

        CTkLabel(self.card_wind, text=card['currency'], font=self.font['h5']).place(x=self.width * 0.35, y=70)
        CTkLabel(self.card_wind, text="Баланс:", font=self.font['h5']).place(x=self.width * 0.15, y=90)
        CTkLabel(self.card_wind, text=card['balance'], font=self.font['h5']).place(x=self.width * 0.35, y=90)
        CTkLabel(self.card_wind, text="Номер карты:", font=self.font['h5']).place(x=self.width * 0.15, y=120)
        CTkLabel(self.card_wind, text=' '.join(card['card_number'][i:i + 4] for i in range(0, len(card['card_number']), 4)), font=self.font['h5']).place(x=self.width * 0.35, y=120)
        CTkLabel(self.card_wind, text="Имя на карте:", font=self.font['h5']).place(x=self.width * 0.15, y=140)
        CTkLabel(self.card_wind, text=card['owner_card'], font=self.font['h5']).place(x=self.width * 0.35, y=140)
        CTkLabel(self.card_wind, text="Годна до:", font=self.font['h5']).place(x=self.width * 0.15, y=160)
        CTkLabel(self.card_wind, text=card['valid_to'], font=self.font['h5']).place(x=self.width * 0.35, y=160)
        CTkLabel(self.card_wind, text="cvv:", font=self.font['h5']).place(x=self.width * 0.15, y=180)
        CTkLabel(self.card_wind, text=card['cvv'], font=self.font['h5']).place(x=self.width * 0.35, y=180)
        secret_frame = CTkFrame(self.card_wind, width=200, height=80, fg_color="gray")
        secret_frame.place(x=175, y=120)
        CTkButton(self.card_wind, text="Показать", command=secret_frame.destroy).place(x=self.width * 0.35, y=220)
        CTkButton(self.card_wind, text="Удалить карту", fg_color="red", width=14, hover_color="pink",
                  command=lambda: delete_card(card['card_number'])).place(x=self.width * 0.75, y=220)
        CTkLabel(self.card_wind, text="Переводы:", font=self.font['h3']).place(x=self.width * 0.15, y=270)
        CTkLabel(self.card_wind, text="Перевести по:", font=self.font['h5']).place(x=self.width * 0.20, y=300)

        self.adr_entry = CTkEntry(self.card_wind)
        label1 = CTkLabel(self.card_wind, text="Номер Телефона:", font=self.font['h5'])
        transaction_type = CTkComboBox(self.card_wind,
                                       values=["Телефону", "Номеру карты", "На свой счет"],
                                       command=partial(change_label,  label1),
                                       width=200)

        transaction_type.place(x=self.width * 0.45, y=300)
        label1.place(x=self.width * 0.20, y=335)
        self.adr_entry.place(x=self.width * 0.45, y=335)
        CTkLabel(self.card_wind, text="Сумма:", font=self.font['h5']).place(x=self.width * 0.20, y=380)
        sum_entry = CTkEntry(self.card_wind)
        sum_entry.place(x=self.width * 0.45, y=380)
        CTkLabel(self.card_wind, text=card['currency'], font=self.font['h5']).place(x=self.width * 0.73, y=383)

        CTkButton(self.card_wind, text="Перевести",
                  command=lambda: transfer(
                                    card['card_number'],
                                    self.adr_entry.get(),
                                    sum_entry.get(),
                                    transaction_type.get()
                                )
                  ).place(x=self.width * 0.20, y=420)
        CTkLabel(self.card_wind, text="Мультиволютные платежи можно совершать только \nмежду своими счетами", font=self.font["p"]).place(x=self.width * 0.15, y=460)

        CTkButton(self.card_wind, text="Закрыть", fg_color="red", hover_color="pink", command=self.card_wind.destroy).place(x=self.width * 0.35, y=620)


        self.card_wind.grab_set()


    def build_main_tab(self):
        CTkLabel(self.main_tab, text="Мои продукты", font=self.font['h1']).place(x=self.width*0.35, y=20)

        CTkButton(self.main_tab,
                text="Создать \nновый",
                width=80,
                height=50,
                font=self.font['p'],
                command=self.show_create_fin_window
                ).place(x=160, y=60)

        CTkButton(self.main_tab,
                text="Настройки",
                width=80,
                height=50,
                font=self.font['p'],
                command=self.open_popup
                ).place(x=260, y=60)

        cards = self.user_data['cards']

        for i, card in enumerate(cards):
            card_frame = CTkFrame(self.main_tab, width=200, height=100, fg_color="gray73", corner_radius=10)
            CTkLabel(card_frame, text=card['type'], font=self.font['h5'], text_color="black").place(x=7, y=0)
            CTkLabel(card_frame, text=' '.join(card['card_number'][i:i+4] for i in range(0, len(card['card_number']), 4)), font=self.font['h5'], text_color="black").place(x=7, y=20)
            CTkLabel(card_frame, text=card['currency'], font=self.font['h5'], text_color="black").place(x=165, y=72)
            CTkLabel(
                card_frame,
                text=card['balance'].rjust(10),
                font=("Roboto Mono", 16, "bold"),  # настоящий моноширинный
                text_color="black",
                anchor="e",  # выравнивание текста вправо
                width=100,  # ширина области под текст
            ).place(x=65, y=72)
            CTkButton(card_frame, text="Открыть", width=5, command=partial(self.on_card_click, card)).place(x=10, y=68)
            card_frame.place(x=40 + 220*(i%2), y=130 + 110*(i//2))

    def quit_account_proccesing(self):
        quit_account()
        self.app.after(0, self.tabview.destroy)
        self.app.after(0, self.non_authorizate_buid)

    def build_personal_account(self):
        print("Построение личного кабинета, данные:", self.user_data)  # Отладочная информация
        if not self.user_data:
            print("Данные пользователя пустые!")  # Отладочная информация
            return

        CTkLabel(self.personal_account, text="Личный кабинет", font=self.font['h1']).place(x=self.width*0.33, y=50)

        CTkLabel(self.personal_account, text=f"Имя:",  font=self.font['h5']).place(x=70, y=120)
        CTkLabel(self.personal_account, text=f"{self.user_data.get('name', 'Не указано')}", font=self.font['p']).place(x=150, y=120)

        CTkLabel(self.personal_account, text=f"Фамилия:",  font=self.font['h5']).place(x=70, y=150)
        CTkLabel(self.personal_account, text=f"{self.user_data.get('surname', 'Не указано')}", font=self.font['p']).place(x=150, y=150)

        CTkLabel(self.personal_account, text=f"Телефон:",  font=self.font['h5']).place(x=70, y=180)
        CTkLabel(self.personal_account, text=f"{self.user_data.get('telephone', 'Не указано')}",  font=self.font['p']).place(x=150, y=180)

        CTkLabel(self.personal_account, text=f"Паспорт:",  font=self.font['h5']).place(x=70, y=210)
        CTkLabel(self.personal_account, text=f"{self.user_data.get('passport_number', 'Не указано')}",  font=self.font['p']).place(x=150, y=210)

        CTkLabel(self.personal_account, text=f"Кол-во счетов:", font=self.font['h5']).place(x=70, y=240)
        CTkLabel(self.personal_account, text=f"{len(self.user_data.get('cards', []))}",  font=self.font['p']).place(x=180, y=240)

        CTkButton(self.personal_account, text="Выход", fg_color="red", hover_color="pink", command=self.app.quit).place(x=280, y=210)

        CTkButton(self.personal_account, text="Выйти из аккаунта", hover_color="pink", fg_color="red", command=self.quit_account_proccesing).place(x=280, y=240)

        CTkLabel(self.personal_account, text=f"Наши офисы: ",  font=self.font['h2']).place(x=70, y=330)
        self.map_widget = TkinterMapView( self.personal_account, width=370, height=250, corner_radius=0)
        self.map_widget.set_position(53.847624, 27.481477)
        self.map_widget.set_zoom(15)
        self.map_widget.place(x=70, y=360)
        self.map_widget.set_marker(53.847624, 27.481477, text="Наш офис")
        self.map_widget.zoom_delta = 0.1

    def start_registration(self, name, surname, passport_number, passport, phone, password):
        def run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(registration(name, surname, passport_number, passport, phone, password))
                self.app.after(0, self.success_auth)
            except Exception as e:
                self.app.after(0, self.open_popup, str(e))
            finally:
                loop.close()

        threading.Thread(target=run, daemon=True).start()

    def success_auth(self):
        def run():
            try:
                self.update_user_data()
                self.app.after(20, self._success_auth_ui)
            except Exception as e:
                self.app.after(0, self.open_popup, str(e))

        threading.Thread(target=run, daemon=True).start()

    def _success_auth_ui(self):
        self.tabview_unauth.destroy()
        self.authorizate_buid()

    def login(self, phone, password):
        def run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                answer = loop.run_until_complete(login(phone, password))
                if answer:
                    self.app.after(0, self.success_auth)
            except Exception as e:
                self.app.after(0, self.open_popup, str(e))
            finally:
                loop.close()

        threading.Thread(target=run, daemon=True).start()

    def non_authorizate_buid(self):
        #делаю без self, чтобы сборщик мусора удалил объекты после прохождения
        self.tabview_unauth = CTkTabview(self.app, anchor="s")
        self.tabview_unauth.pack(expand=True, fill='both')

        authorizate_tab = self.tabview_unauth.add("Авторизация")
        registrate_tab = self.tabview_unauth.add("Регистрация")

        phone = CTkEntry(authorizate_tab, placeholder_text="Номер телефона")
        password = CTkEntry(authorizate_tab, placeholder_text="Пароль")

        CTkLabel(authorizate_tab, text="Авторизация", anchor="s", font=self.font['h1']).place(x=self.width*0.37, y=200)
        phone.place(x=self.width*0.36, y=250)
        password.place(x=self.width*0.36, y=300)
        CTkButton(
            authorizate_tab,
            text="Войти",
            command=lambda: self.login(phone.get(), password.get())
                                                ).place(x=self.width * 0.36, y=350)


        CTkLabel(registrate_tab, text="Регистрация", font=self.font['h1']).place(x=self.width*0.37, y=100)
        name = CTkEntry(registrate_tab, placeholder_text="Имя")
        surname = CTkEntry(registrate_tab, placeholder_text="Фамилия")
        passport_number = CTkEntry(registrate_tab, placeholder_text="Паспорт(Серия и номер)")
        passport = CTkEntry(registrate_tab, placeholder_text="Паспорт(индефикационный номер)")

        rphone = CTkEntry(registrate_tab, placeholder_text="Телефон")
        rpassword = CTkEntry(registrate_tab, placeholder_text="Пароль")

        name.place(x=self.width*0.36, y=150)
        surname.place(x=self.width*0.36, y=200)
        passport_number.place(x=self.width*0.36, y=250)
        passport.place(x=self.width*0.36, y=300)
        rphone.place(x=self.width*0.36, y=400)
        rpassword.place(x=self.width*0.36, y=450)
        CTkButton(
            registrate_tab,
            text="Зарегистрироваться",
            command= lambda : self.start_registration(name.get(), surname.get(),
                             passport_number.get(), passport.get(),
                             rphone.get(), rpassword.get())

        ).place(x=self.width * 0.36, y=550)

    def open_popup(self, e, tittle="Ошибка"):
        text = str(e)
        # Создание всплывающего окна в главном потоке
        self.app.after(0, self._open_popup, text, tittle)

    def _open_popup(self, text, tittle="Ошибка"):
        popup = CTkToplevel(self.app)
        popup.title(tittle)
        popup.geometry("400x200")

        CTkLabel(popup, text=text, anchor="center").pack(pady=20)

        CTkButton(popup, text="Закрыть", command=popup.destroy).pack(pady=10)

        # Блокируем основное окно, пока popup открыт
        popup.grab_set()






