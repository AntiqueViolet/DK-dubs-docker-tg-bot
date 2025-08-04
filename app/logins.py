import requests
from urllib.parse import urljoin
import config


def logging(a, b):
    headers1 = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
        "cache-control": "max-age=0",
        "content-type": "application/x-www-form-urlencoded",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Microsoft Edge";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "Referer": "https://drive-dk.com/",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

    headers2 = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
        "cache-control": "max-age=0",
        "sec-ch-ua": "\"Not(A:Brand\";v=\"99\", \"Microsoft Edge\";v=\"133\", \"Chromium\";v=\"133\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "Referer": "https://drive-dk.com/",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

    session = requests.Session()
    session.headers.update(headers1)
    session.cookies.update(config.COOKIE1)

    try:
        form_data = {
            "_username": config.DRIVE_LOGIN,
            "_password": config.DRIVE_PASSW,
            "_submit": "Войти"
        }

        login_response = session.post(
            url="https://drive-dk.com/login_check",
            data=form_data,
            allow_redirects=False
        )

        print(f"[1] POST /login_check: Status {login_response.status_code}")

        redirect_url = urljoin(login_response.url, login_response.headers["Location"])
        print(redirect_url)

        session.headers.update(headers2)
        session.cookies.update(config.COOKIE2)

        agreement_response = session.get(redirect_url, allow_redirects=False)
        print(f"[2] GET /to/agreement: Status {agreement_response.status_code}")

        final_url = urljoin(agreement_response.url, agreement_response.headers["Location"])
        final_response = session.get(final_url)
        print(final_url)
        print(f"[3] GET /lk: Status {final_response.status_code}")

        if final_response.status_code == 200 and final_response.url == config.TARGET_URL:
            print("Успешная авторизация")
        else:
            print(f"\nОшибка: {final_response.status_code}")

        dk_url = f'https://drive-dk.com/to/dk/downloadZip/{a}'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Sec-CH-UA': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Cookie': config.COOKIE_STRING_FINAL
        }

        response = requests.get(dk_url, headers=headers)
        filename = ''
        if response.status_code == 200:
            content_disposition = response.headers.get('Content-Disposition')
            if content_disposition and 'filename=' in content_disposition:
                filename = f"{b}.pdf"

            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f'Файл "{filename}" успешно скачан')
        else:
            print(f'Ошибка загрузки. Код статуса: {response.status_code}')

    except Exception as e:
        with open("logss.txt", 'w') as f:
            f.write(str(e))
        print(f"\nКрит: {str(e)}")