"""Парсеры."""

import logging
import re
from collections import defaultdict
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEP_DOC_URL,
                       PEPS_NUMERICAL_URL)
from outputs import control_output
from utils import find_tag, get_response, get_soup


def whats_new(session):
    """Парсер статей о нововедениях в Python."""
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = get_soup(session, whats_new_url)
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        soup = get_soup(session, version_link)
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))
    return results


def latest_versions(session):
    """Парсер статуса версии Python."""
    soup = get_soup(session, MAIN_DOC_URL)
    sidebar = find_tag(
        soup, 'div', attrs={'class': 'sphinxsidebarwrapper'}
    )
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось')

    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((link, version, status))
    return results


def download(session):
    """Парсер скачивающий документацию Python."""
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = get_soup(session, downloads_url)
    main_tag = find_tag(soup, 'div', attrs={'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_a4_link = pdf_a4_tag['href']

    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]

    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = get_response(session, archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    """Парсер документации PEP."""
    results = [('Статус', 'Количество')]
    actual_statuses = defaultdict(int)

    soup = get_soup(session, PEPS_NUMERICAL_URL)
    section_tag = find_tag(soup, 'section')
    tbody_tag = find_tag(section_tag, 'tbody')
    tr_tag = tbody_tag.find_all('tr')

    for tr in tqdm(tr_tag):
        table_status = find_tag(tr, 'abbr').text[1:]

        if table_status is None:
            return

        pep_link = find_tag(tr, 'a')['href']
        pep_page_url = urljoin(PEP_DOC_URL, pep_link)
        soup = get_soup(session, pep_page_url)
        dl_tag = find_tag(soup, 'dl')
        page_status = dl_tag.find(
            string='Status').parent.find_next_sibling('dd').string

        if page_status is None:
            return

        actual_statuses[page_status] += 1

        if page_status not in EXPECTED_STATUS[table_status]:
            error_msg = (
                'Несовпадающие статусы:\n'
                f'{pep_page_url}\n'
                f'Статус в карточке {page_status}\n'
                f'Ожидаемые статусы: {EXPECTED_STATUS[table_status]}'
            )
            logging.warning(error_msg)

    for status, quantity in actual_statuses.items():
        results.append((status, quantity))

    results.append(('Total', sum(actual_statuses.values())))
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    """Главная функция парсера."""
    configure_logging()
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    results = MODE_TO_FUNCTION[args.mode](session)
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
