from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import PySimpleGUI as SG
import sqlite3
import os
from time import sleep
conn = sqlite3.connect('settings.db')
cursor = conn.cursor()
time_to_sleep = 1.4
warning_window = SG.Window('Предупреждение', [
    [SG.Text('Вы не настроили программу. Программа не будет коректно работать.')],
    [SG.Button('Настроить')]
])


def setting(first_launch=False, last_widow=None): #part_start: Настройки.
    #setup:заготовки окон.
    setting_loadout = [

        [SG.Text('Путь к chromedriver.')],
        [SG.In(), SG.FileBrowse()],
        [SG.Text('Имя пользователя.')],
        [SG.In()],
        [SG.Text('Список номеров.')],
        [SG.In(), SG.FileBrowse()],
        [SG.Text('Текст рассылки.')],
        [SG.In(), SG.FileBrowse()],
        [SG.Text()],
        [SG.Button('Сохранить'), SG.Button('Удалить настройки')],
        [ SG.Output(size=(55, 4), key='-OUTPUT-')],
        [SG.Button('Закрыть')]

    ]

    first_start_loadout = [

        [SG.Text('Перед первым запуском программы, заполните настройки.')],
        [SG.Text('')],
        [SG.Text('Путь к chromedriver.')],
        [SG.In(), SG.FileBrowse()],
        [SG.Text('Имя пользователя.')],
        [SG.In()],
        [SG.Text('Список номеров.')],
        [SG.In(), SG.FileBrowse()],
        [SG.Text('Текст рассылки.')],
        [SG.In(), SG.FileBrowse()],
        [SG.Text()],
        [SG.Button('Сохранить')],
        [SG.Output(size=(30, 3), key='-OUTPUT-')],
        [SG.Button('Продолжить'), SG.Button('Выйти')]

    ] #setup:заготовки окон.

    if first_launch == True:
        window = SG.Window('Настройки', first_start_loadout)

    elif first_launch == False:
        window = SG.Window('Настройте программу',setting_loadout)


    while True:

        event, values = window.read()
        values_list = [values[0], values[1], values[2], values[3]]

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS settings(

                id             INTEGER NOT NULL PRIMARY KEY,
                chromedriver   VARCHAR(255) NOT NULL,
                profile        VARCHAR(255) NOT NULL,
                numbers        VARCHAR(255) NOT NUll,
                text           VARCHAR(255) NOT NUll
            )
            ''')

        if event in 'Сохранить':
            cursor.execute("insert into settings (chromedriver, profile, numbers, text) values ( ? , ? , ? , ? )",
                           values_list)
            conn.commit()

            window['-OUTPUT-'].update('Данные сохранены.')

        if event in 'Удалить настройки':
            cursor.execute('DROP TABLE settings')
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS settings(
                    id             INTEGER NOT NULL PRIMARY KEY,
                    chromedriver   VARCHAR(255) NOT NULL,
                    profile        VARCHAR(255) NOT NULL,
                    numbers        VARCHAR(255) NOT NUll,
                    text           VARCHAR(255) NOT NUll

                )
                ''')
            conn.commit()

            window['-OUTPUT-'].update('ВНИМАНИЕ: после удаления настроек, нужно снова их заполнить. Иначе программа не будет работать!')

        if event in 'Продолжить':
            window.close()
            windows()

        if event in 'Закрыть':
            window.close()
            windows()

        if event in 'Выйти':
            raise SystemExit

        #part_end: Настройки.

def end_of_mailing_window(): #part_start: Окно: появляется в конце рассылки. Может вернуть к выбору месседжера или закончить работу программы.

    #setup: заготовка окна.
    end_of_mailing_loadout = [

        [SG.Button('Вернуться к выбору месседжера, для рассылки'), SG.Button('Выход')]

    ] #setup: заготовка окна.

    end_of_mailing_window = SG.Window('Конец рассылки', end_of_mailing_loadout)

    while True:

        event, values = end_of_mailing_window.read()

        if event == 'Вернуться к выбору месседжера, для рассылки':
            end_of_mailing_window.close()
            windows()

        if event == 'Выход':
            conn.close()
            return SystemExit

    # part_end: Окно: появляется в конце рассылки. Может вернуть к выбору месседжера или закончить работу программы.

def windows():

    try: #part_start: Отсюда начинается работа программы. Обрабатывают записаные номера.
        #setup: db.
        cursor.execute("SELECT numbers FROM settings")
        db = cursor.fetchone()

        with open(db[0], 'r', encoding="utf-8") as numbers:
            numbers = numbers.readlines()

        for index, element in enumerate(numbers):
            numbers[index] = element.replace('\n', '')

        for index, element in enumerate(numbers):

            if numbers[index][0] in '8':
                numbers[index] = element.replace('8', '7', 1).replace('\n', '')

            if numbers[index][0] in '+':
                numbers[index] = element.replace('+', '', ).replace('\n', '')

        cursor.execute("SELECT chromedriver, profile, text FROM settings")
        db = cursor.fetchone()
        #setup: db.

        with open(db[2], 'r', encoding="utf-8") as text:
            text = text.readlines()

        for index, edit in enumerate(text):
            text[index] = edit.replace('\n', '')

        text = ' '.join(text)

    except:
        setting(True) #part_in_part: Открываются настройки, если програ впервые запускается. Ексептит работу db.
        #part_end: Отсюда начинается работа программы. Обрабатывают записаные номера.


    # setup: заготовка окна.
    start_window = SG.Window('Рассылка', [
        [SG.Text('Выберите месседжер для рассылки.')],
        [SG.Button('Whatsapp'), SG.Button('Telegram'), SG.Button('Вконтакте'), SG.Text(''), SG.Button('Настройки'),
         SG.Button('Выход')]
    ]) #setup: заготовка окна.


    while True:  # part_start: Выбор соцсети, где будет вестись

        event, values = start_window.read()

        if event in 'Whatsapp':
            start_window.close()
            SG.popup_quick_message('Сейчас появится окно прогресса.')

            for number in numbers:
                full_progress_bar = len(numbers)
                progress = 0

                whatsapp(number, text)
                SG.OneLineProgressMeter('Прогресс выполнения рассылки.', progress + 1, full_progress_bar, 'key', no_titlebar=True)

                progress += 1

            return end_of_mailing_window()

        if event in 'Telegram':
            SG.popup_quick_message('Сейчас появится окно прогресса.')
            start_window.close()

            telegram(numbers, text)

            return end_of_mailing_window()

        if event in 'Вконтакте':
            SG.popup_quick_message('Сейчас появится окно прогресса.')
            start_window.close()

            vk()

            return end_of_mailing_window()

        if event in 'Настройки':
            start_window.close()
            setting()

        if event in 'Выход':
            conn.close()
            raise SystemExit

    # part_end:  Выбор соцсети, где будет вестись



def check_exists_by_xpath(driver, xpath):#part: Смотрит, существует ли элемент.

    try:

        sleep(time_to_sleep)
        driver.until(EC.presence_of_element_located((By.XPATH, xpath)))

    except:

        return False

    return True





def whatsapp(number, text): #part_start: рассылка на вотс.
    #setup:
    cursor.execute("SELECT chromedriver, profile FROM settings")
    db = cursor.fetchone()

    os.system("TASKKILL /F /IM chrome.exe")

    options = webdriver.ChromeOptions()
    options.add_argument('--user-data-dir=C:\\Users\{}\AppData\Local\Chromium\\User Data'.format(db[1]))
    #options.add_argument('headless') #FixMe: При включенном headless, парсер перестает рабоать.
    driver = webdriver.Chrome(executable_path='{}'.format(db[0]), chrome_options=options)
    driver_delay = WebDriverWait(driver, 10)

    driver.get('https://web.whatsapp.com/send?phone={}'.format(number))
    #setup:



    if check_exists_by_xpath(driver_delay, '//*[@id="app"]/div/div/div[2]/div[1]/div/div[2]/div/canvas'): #Эксептит вход в вотс.

        SG.popup_ok('ОШИБКА: Войдите в What#part_start: рассылка на вотс.sapp Web перед рассылкой сообщений.')
        driver.quit()
        windows()

    sleep(time_to_sleep)
    if check_exists_by_xpath(driver_delay, '//*[@id="app"]/div/span[2]/div/div/div/div/div/div/div[2]/div'): #Эксептит одно всплывающее окно, на которое переходит фокус селены.

        driver_delay.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/span[2]/div/div/div/div/div/div/div[2]/div'))).click()

    sleep(time_to_sleep)
    driver_delay.until(EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div[2]/div/div[2]'))).click()

    sleep(time_to_sleep)
    driver_delay.until(EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div[2]/div/div[2]'))).send_keys('{}'.format(text))

    sleep(time_to_sleep)
    driver_delay.until(EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div[3]/button'))).click()

    sleep(time_to_sleep)
    driver.quit() #part_end: рассылка на вотс.




def telegram(numbers, text): #part_start: рассылка на телегу.
    #setup:
    cursor.execute("SELECT chromedriver, profile FROM settings")
    db = cursor.fetchone()

    os.system("TASKKILL /F /IM chrome.exe")

    options = webdriver.ChromeOptions()
    options.add_argument('--profile-directory=Default')
    options.add_argument('--user-data-dir=C:/Users/{}/AppData/Local/Google/Chrome/User Data'.format(db[1]))
    #options.add_argument('headless') #FixMe: При включенном headless, парсер перестает рабоать.
    driver = webdriver.Chrome(executable_path='{}'.format(db[0]), chrome_options=options)
    driver_delay = WebDriverWait(driver, 10)

    driver.get('https://web.telegram.org/#/im')
    #setup:




    def send_keys_to(xpath, key):#Part_in_Part: пишет в строку и нажимает Enter. Решает проблему с прогрузкой элемента.

        while True:

            try:

                ActionChains(driver).send_keys_to_element(driver_delay.until(EC.presence_of_element_located((By.XPATH, xpath))), key, Keys.ENTER).perform()

            except:

                pass

            break


    if check_exists_by_xpath(driver_delay, '//*[@id="ng-app"]/body/div[1]/div/div[2]/div[2]/form/h3') == True: #Эксептит вход в телегу.
        SG.popup_ok('ОШИБКА: Войдите в Telegram Web перед рассылкой сообщений.')
        driver.quit()
        windows()

    full_progress_bar = len(numbers)
    progress = 0

    for number in numbers: #Part_in_Part: Самое мясо. Сдесь произходит сама рассылка, нажимаются кнопочки и тд.

        driver_delay.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ng-app"]/body/div[1]/div[1]/div/div/div[1]/div/a'))).click()

        sleep(time_to_sleep)
        driver_delay.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ng-app"]/body/div[1]/div[1]/div/div/div[1]/div/ul/li[2]/a'))).click()

        sleep(time_to_sleep)
        driver_delay.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ng-app"]/body/div[6]/div[2]/div/div/div[3]/div/button'))).click()

        sleep(time_to_sleep)
        send_keys_to('//*[@id="ng-app"]/body/div[7]/div[2]/div/div/div[1]/form/div[1]/input', number) # Вписывает номер в строку.

        sleep(time_to_sleep)
        send_keys_to('//*[@id="ng-app"]/body/div[1]/div[2]/div/div[2]/div[3]/div/div[3]/div[2]/div/div/div/form/div[2]/div[5]', text)

        sleep(time_to_sleep)
        SG.OneLineProgressMeter('Прогресс выполнения рассылки.', progress + 1, full_progress_bar, 'key', no_titlebar=True)
        progress += 1

    driver.quit() #part_end: рассылка на телегу.




def vk(): #TODO: сделать рассылку вк.
    #setup:
    cursor.execute("SELECT chromedriver, profile FROM settings")
    db = cursor.fetchone()

    os.system("TASKKILL /F /IM chrome.exe")

    options = webdriver.ChromeOptions()
    options.add_argument('--user-data-dir=C:\\Users\{}\AppData\Local\Chromium\\User Data'.format(db[1]))
    options.add_argument('headless')
    driver = webdriver.Chrome(executable_path='{}'.format(db[0]), chrome_options=options)
    driver_delay = WebDriverWait(driver, 10)

    #driver.get('')
    #setup:


    SG.popup_quick('Скоро здесь что нибудь будет.')

    driver.quit() #TODO: сделать рассылку вк.





if __name__ == '__main__':

    windows()
    conn.close()
