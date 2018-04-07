from urllib.request import Request, urlopen
from datetime import datetime
from PyPDF2 import PdfFileWriter, PdfFileReader
from io import BytesIO

import os.path
import re
import subprocess

BASE_URL = "https://sites.google.com/site/fedorestbe/menu-fr/menu-noga-fr/noga_fr_{}_{}.pdf"
BASE_PDF_PATH = "{}-{}.pdf"
BASE_TXT_PATH = "{}-{}.txt"
BASE_DAILY_TXT_PATH = "{}-{}-{}.txt"
HEADERS_REGEX = [r'^Potage$', r'^Plat du jour', r'^Plat Végétarien', r'^Grill']

def get_date():
	""" Return the current day of week (0-6), the current week (0-51) and the current year"""
	today = datetime.today()
	day = today.weekday()
	day = 2 # TODO : remove, test purpose only
	week = today.isocalendar()[1]
	year = today.year
	return (day, week, year)

def download_pdf():
	""" Download the current menu as PDF """
	(_, week, year) = get_date()
	url = BASE_URL.format(week, year)
	path = BASE_PDF_PATH.format(year, week)

	remote = urlopen(Request(url)).read()
	file = BytesIO(remote)
	pdf = PdfFileReader(file)
	writer = PdfFileWriter()
	writer.addPage(pdf.getPage(0))
	with open(path, "wb") as out:
		writer.write(out)

def get_pdf_path():
	""" Return the path to the current menu as PDF, download the PDF if necessary """
	(_, week, year) = get_date()
	path = BASE_PDF_PATH.format(year, week)

	if not os.path.exists(path):
		download_pdf()

	return path

def create_txt():
	""" Create the current menu as TXT """
	(_, week, year) = get_date()
	pdf_path = get_pdf_path()
	txt_path = BASE_TXT_PATH.format(year, week)
	subprocess.call(['pdftotext', pdf_path, txt_path])


def get_txt_path():
	""" Return the path of the current menu as TXT, create the TXT if necessary """
	(_, week, year) = get_date()
	path = BASE_TXT_PATH.format(year, week)

	if not os.path.exists(path):
		create_txt()
	
	return path

def get_week_menu():
	""" Return the content of this week menu """
	with open(get_txt_path(), 'r', encoding='utf-8') as menu:
		lines = menu.readlines()[4:]
		for line in lines:
			yield line

def parse_week_menu():
	""" Parse the weekly menu and split it into 5 files, one for each day """

	(day, week, year) = get_date()
	today_menu_path = BASE_DAILY_TXT_PATH.format(year, week, day)

	if os.path.exists(today_menu_path):
		return

	menus = ["", "", "", "", ""]
	closed = [False, False, False, False, False]
	skip_meal = [False, False, False, False, False]
	i = 0

	for line in get_week_menu():
		line = line.strip()
		if line == '':
			i += 1
			i = i % 5
			continue

		if skip_meal[i] or closed[i]:
			i += 1
			i = i % 5

		header = False
		for regex in HEADERS_REGEX:
			if re.match(regex, line, flags=re.S|re.M):
				menus[i] += "\n**" + line + "**\n"
				header = True
				skip_meal = [False, False, False, False, False]
				break

		if not header:
			if line == 'Fermé':
				print('closed : {}'.format(i))
				closed[i] = True
			elif line == 'Non disponible':
				skip_meal[i] = True
			
			menus[i] += line + '\n'
			
	for i, day_menu in enumerate(menus):
		with open(BASE_DAILY_TXT_PATH.format(year, week, i), 'w', encoding='utf-8') as out:
			out.write(day_menu)

def get_today_menu():
	""" Get the menu for today """
	(day, week, year) = get_date()

	if day < 0 or day > 4:
		return "C'est le weekend aujourd'hui..."

	today_menu_path = BASE_DAILY_TXT_PATH.format(year, week, day)

	if not os.path.exists(today_menu_path):
		parse_week_menu()

	with open(today_menu_path, 'r', encoding='utf-8') as menu:
		return menu.read()

get_today_menu()