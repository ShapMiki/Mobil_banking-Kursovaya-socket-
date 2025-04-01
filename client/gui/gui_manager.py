from customtkinter import *
from json import load
import asyncio
import threading

from communicate.client import client
from communicate.service import *


class GUIManager:
    def __init__(self):
        self.app = CTk()
        self.app.title("МБанкинг")
        self.width = 500
        self.height = 700
        self.app.geometry(f"{self.width}x{self.height}")

        self.config = {}
        with open("data/client_config.json", "r") as json_file:
            self.config = load(json_file)

        self.font = self.config['font']
        for i in self.font:
            self.font[i] = tuple(self.font[i])

    def main(self):
        #TODO: Сделать проверку на авторизацию
        #self.authorizate_buid()
        self.non_authorizate_buid()

        self.app.mainloop()



    def authorizate_buid(self):
        self.tabview = CTkTabview(self.app, anchor="s")
        self.tabview.pack(expand=True, fill='both')

        self.payment_tab = self.tabview.add("Платежи")
        self.main_tab = self.tabview.add("Главная")
        self.personal_account = self.tabview.add("Кабинет")






    def start_registration(self, name, surname, passport_number, passport, phone, password):
        def run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(registration(name, surname, passport_number, passport, phone, password))
                self.app.after(0, self.success_registration)
            except Exception as e:
                self.app.after(0, self.open_popup, str(e))
            finally:
                loop.close()

        threading.Thread(target=run, daemon=True).start()

    def success_registration(self):
        self.tabview_unauth.destroy()
        asyncio.create_task(self.authorizate_buid())

    def login(self, phone, password):
        def run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                answer = loop.run_until_complete(login(phone, password))
                if answer:
                    self.app.after(0, self.success_login)
            except Exception as e:
                self.app.after(0, self.open_popup, str(e))
            finally:
                loop.close()

        threading.Thread(target=run, daemon=True).start()

    def success_login(self):
        self.tabview_unauth.destroy()
        asyncio.create_task(self.authorizate_buid())


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

    def open_popup(self, text):
        # Создание всплывающего окна в главном потоке
        self.app.after(0, self._open_popup, text)

    def _open_popup(self, text):
        popup = CTkToplevel(self.app)
        popup.title("Ошибка")
        popup.geometry("300x200")

        CTkLabel(popup, text=text, anchor="center").pack(pady=20)

        CTkButton(popup, text="Закрыть", command=popup.destroy).pack(pady=10)

        # Блокируем основное окно, пока popup открыт
        popup.grab_set()






