from customtkinter import *
from json import load
import asyncio
import threading

from communicate.client import client
from communicate.service import *
from tkintermapview import TkinterMapView


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
        except Exception as e:
            self.open_popup(e)

    def authorizate_buid(self):
        self.update_user_data()
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

    def build_main_tab(self):
        pass

    def quit_account_proccesing(self):
        quit_account()
        self.app.after(0, self.tabview.destroy)
        self.app.after(0, self.non_authorizate_buid)



    def build_personal_account(self):
        CTkLabel(self.personal_account, text="Личный кабинет", font=self.font['h1']).place(x=self.width*0.33, y=50)

        CTkLabel(self.personal_account, text=f"Имя:",  font=self.font['h5']).place(x=70, y=120)
        CTkLabel(self.personal_account, text=f"{self.user_data['name']}", font=self.font['p']).place(x=150, y=120)

        CTkLabel(self.personal_account, text=f"Фамилия:",  font=self.font['h5']).place(x=70, y=150)
        CTkLabel(self.personal_account, text=f"{self.user_data['surname']}", font=self.font['p']).place(x=150, y=150)

        CTkLabel(self.personal_account, text=f"Телефон:",  font=self.font['h5']).place(x=70, y=180)
        CTkLabel(self.personal_account, text=f"{self.user_data['telephone']}",  font=self.font['p']).place(x=150, y=180)

        CTkLabel(self.personal_account, text=f"Паспорт:",  font=self.font['h5']).place(x=70, y=210)
        CTkLabel(self.personal_account, text=f"{self.user_data['passport_number']}",  font=self.font['p']).place(x=150, y=210)

        CTkLabel(self.personal_account, text=f"Кол-во счетов:", font=self.font['h5']).place(x=70, y=240)
        CTkLabel(self.personal_account, text=f"{len(self.user_data['cards'])}",  font=self.font['p']).place(x=180, y=240)


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
        self.update_user_data()
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

    def open_popup(self, e):
        text = str(e)
        # Создание всплывающего окна в главном потоке
        self.app.after(0, self._open_popup, text)

    def _open_popup(self, text):
        popup = CTkToplevel(self.app)
        popup.title("Ошибка")
        popup.geometry("400x200")

        CTkLabel(popup, text=text, anchor="center").pack(pady=20)

        CTkButton(popup, text="Закрыть", command=popup.destroy).pack(pady=10)

        # Блокируем основное окно, пока popup открыт
        popup.grab_set()






