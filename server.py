import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


class SimpleHandler(BaseHTTPRequestHandler):
    """Обработчик HTTP-запросов."""

    # Маппинг маршрутов к файлам
    ROUTES = {
        '/': 'templates/index.html',
        '/contacts': 'templates/contacts.html',
    }

    def _send_html_response(self, status_code: int, file_path: str) -> None:
        """Читает HTML-файл через контекстный менеджер и отправляет клиенту."""
        try:
            # Чтение через with open()
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().encode('utf-8')

            self.send_response(status_code)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            # Если даже файл ошибки не найден — возвращаем минимальный ответ
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'Internal Server Error')

    def do_GET(self):
        """Обработка GET-запросов."""
        path = urlparse(self.path).path

        if path in self.ROUTES:
            self._send_html_response(200, self.ROUTES[path])
        else:
            # Для любых неизвестных маршрутов — 404
            self._send_html_response(404, 'templates/404.html')

    def do_POST(self):
        """Обработка POST-запросов. Данные выводятся в консоль."""
        path = urlparse(self.path).path

        # Читаем тело запроса
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')

        # Парсим данные формы (application/x-www-form-urlencoded)
        parsed_data = parse_qs(body)

        # Выводим в консоль.
        print('\n' + '=' * 50)
        print(f'📩 POST-запрос на: {path}')
        print(f'📋 Полученные данные: {parsed_data}')
        print('=' * 50 + '\n')

        # После отправки формы — возвращаем страницу контактов
        if path in self.ROUTES:
            self._send_html_response(200, self.ROUTES[path])
        else:
            self._send_html_response(404, 'templates/404.html')

    def log_message(self, format, *args):
        """Переопределяем логирование, чтобы видеть запросы в консоли."""
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_server(host: str = 'localhost', port: int = 8000) -> None:
    server = HTTPServer((host, port), SimpleHandler)
    print(f'🚀 Сервер запущен: http://{host}:{port}')
    print('Нажми Ctrl+C для остановки.')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n🛑 Сервер остановлен.')
        server.server_close()


if __name__ == '__main__':
    run_server()