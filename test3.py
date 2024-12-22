import time
from pynput.keyboard import Listener, Key
from rx.subject import Subject

# Инициализация Subject для слушателей
subscribers = Subject()
terminate_signal = False
current_tab_active = False

# Отправка события всем слушателям
def dispatch_event(event):
    subscribers.on_next(event)

# Отправка ошибки всем слушателям
def dispatch_error(error):
    subscribers.on_error(error)

def log_to_file(file_path):
    def on_next(data):
        # Запись сообщения в файл с отметкой времени
        with open(file_path, 'a', encoding='utf-8') as log:
            log.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {data}\n")

    def on_completed():
        # Запись сообщения о завершении работы трекера
        with open(file_path, 'a', encoding='utf-8') as log:
            log.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Трекинг завершён.\n")

    def on_error(error):
        # Запись сообщения об ошибке
        with open(file_path, 'a', encoding='utf-8') as log:
            log.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Ошибка: {error}\n")

    subscribers.subscribe(on_next, on_error, on_completed)

# Обработка нажатия клавиши
def handle_keypress(key):
    global current_tab_active
    try:
        if key == Key.tab:
            current_tab_active = True

        # Рассылаем событие о нажатии клавиши
        dispatch_event(f"Нажата клавиша: {key}")
    except RuntimeError as error:
        # При ошибке отправляем сообщение об ошибке
        dispatch_error(error)

# Обработка отпускания клавиши
def handle_keyrelease(key):
    global terminate_signal, current_tab_active

    if key == Key.tab:
        current_tab_active = False

    # Рассылаем событие об отпускании клавиши
    dispatch_event(f"Отпущена клавиша: {key}")

    if current_tab_active and key == Key.esc:  # Завершение работы при комбинации Tab + Esc
        terminate_signal = True
        return False

def main():
    global terminate_signal
    log_to_file("keyboard_events.log")  # Инициализация логгера для записи событий

    # Функция для запуска слушателя клавиатуры в отдельном потоке
    def listener_thread():
        with Listener(on_press=handle_keypress, on_release=handle_keyrelease) as listener:
            listener.join()

    listener_thread()

    try:
        while not terminate_signal:
            time.sleep(0.1)
    except KeyboardInterrupt:
        terminate_signal = True
    finally:
        # Сообщаем слушателям, что работа завершена
        subscribers.on_completed()

if __name__ == "__main__":
    main()