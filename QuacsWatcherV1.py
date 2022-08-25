# Copyright (C) 2022 QuacsWatcher V.1

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import requests
import json
from typing import Dict, List
import os

def return_available(sections: List) -> List:
	available = []
	for section in sections:
		if(section["rem"] > 0):
			available.append(section)
	return available

def check_available(courses_dict: Dict, dept: str, crse: str):
	available: List = return_available(courses_dict[dept][crse])
	if len(available) == 0:
		print(f"\tNo sections available for {dept}-{crse}, L + ratio bozo")
	else:
		for sect in available:
			rem: int = sect['rem']
			crn: int = sect['crn']
			sec = sect['sec']
			print(f"\tSection: {sec} | CRN: {crn} | {rem} spots remaining")


def get_recent_data(month: str, year: str) -> bool:
	url = f"https://raw.githubusercontent.com/quacs/quacs-data/master/semester_data/{year}{month}/courses.json"
	etag_file = open(f"{year}{month}_etag.txt", mode="a+")
	etag_file.seek(0)
	local_etag = etag_file.read()
	payload = {"If-None-Match" : local_etag}

	r = requests.get(url, allow_redirects=True, headers=payload)
	if r.status_code == 200:
		json_file = open(f'{year}{month}_courses.json', 'wb')
		json_file.write(r.content)
		json_file.close()
		req_etag = r.headers['etag']
		etag_file.seek(0)
		etag_file.write(req_etag)
	etag_file.close()
	if r.status_code == 200 or r.status_code == 304 or r.status_code == 412:
		return True
	os.remove(f"{year}{month}_etag.txt")
	return False

def construct_courses_dict(month: str, year: str) -> Dict:
	courses_dict = {}
	tags = {}
	json_file = open(f'{year}{month}_courses.json', 'rb')
	courses_json = json.load(json_file)
	for department in courses_json:
		tags["department"] = department["code"]
		courses_dict[tags["department"]] = {}
		for course in department["courses"]:
			tags["course"] = str(course["crse"])
			courses_dict[tags["department"]][tags["course"]] = course["sections"]
	json_file.close()
	return courses_dict
	
def check_directory():
	canon_name: str = "QuacsWatcher"
	current_folder = os.path.basename(os.getcwd())
	if current_folder != canon_name:
		exit(f'Current folder is "{current_folder}", please store script in a folder named "{canon_name}"')

def print_license():
	print("QuacsWatcher V1.1, Copyright (C) 2022 Lorenzo Rivera")
	print("QuacsWatcher comes with ABSOLUTELY NO WARRANTY; for details," +
	" go to: https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html\n\n")

def get_desired(courses_dict: Dict) -> Dict[str, List[str]]:
	print('Now taking input of courses. Type -1 to finish the course selection process.')
	desired_courses: Dict[str, List[str]] = {}
	while True:

		input_course = str(input('\nEnter course in the following format: "DEPT-XXXX"\n')).upper().strip()
		if input_course == "-1":
			print("Finalizing desired courses...")
			break
		elif len(input_course) != 9  or input_course[4] != "-":
			print("Invalid course specifier, try again")
			continue
		input_course = input_course.strip().split('-')

		print(f"Your specified course: {input_course[0]}-{input_course[1]}")

		if input_course[0] not in courses_dict.keys():
			print("Invalid course department code specified, try again.")
			continue
		if input_course[1] not in courses_dict[input_course[0]].keys():
			print("Invalid course specified, try again.")
			continue

		
		confirm: str = ""
		while confirm not in {"Y", "N"}:
			confirm = str(input("Confirm course? Y/N: ")).upper().strip()
		if confirm == "N":
			print("Discarded entry.")
		else:
			if input_course[0] not in desired_courses.keys():
				desired_courses[input_course[0]] = []
			desired_courses[input_course[0]].append(input_course[1])
			print("Added entry.")
	
	return desired_courses

def get_term_course_data() -> Dict:
	term_months = {"spring" : "01", "summer" : "05", "fall" : "09", "winter": "12"}
	while True:
		term: List[str] = str(input('Enter desired school term in the following format: "[Spring/Summer/Fall/Winter] 20XX"\n')).lower().strip().split(" ")
		if len(term) != 2 or term[0] not in term_months.keys():
			print("Invalid school term, please try again")
			continue
		check = get_recent_data(term_months[term[0]], term[1])
		if not check:
			print(f"Semester data for {term[0]} {term[1]} is not available, please try again, or enter another semester.")
		else:
			print("Semester data found, constructing database...")
			break

	return construct_courses_dict(term_months[term[0]], term[1])


def main():
	print_license()
	check_directory()
	courses_dict: Dict = get_term_course_data()	
	desired_courses: Dict[str, List[str]] = get_desired(courses_dict)
	for dept, courses in desired_courses.items():
		print(f"\n{dept} Department courses:")
		for course in courses:
			check_available(courses_dict, dept, course)

if __name__ == "__main__":
    main()