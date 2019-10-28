import os
import time
import sys
import csv
import math
import re

header = ['vendor', 'file_path', 'temperature',
		'command window start', 'command window size', 'command delay',
		'max nok size', 'scan time', 'ds_sht', 'data window size',
		'window arrange', 'window width', 'window flag']

def get_window_arrange(per_str_info_list):
	if '--' in per_str_info:
		line_list = per_str_info.split()
		separator_index = line_list.index('--')
		begin = int(line_list[separator_index - 1], 16)
		end = int(line_list[separator_index + 1], 16)
		size = end - begin + 1
		return size, line_list[-1]
	else:
		return 1, line_list[-1]

def scrub_window_arrange(emmc_info_block):
	window_width_list = []
	window_flag_list = []
	window_string_list = []
	width = 1

	for i in range(0, len(emmc_info_block)):
		if 'current temperature is' in emmc_info_block[i]:
			temp = int(emmc_info_block[i].split()[-1], 10)
		elif 'cmd delay' in emmc_info_block[i]:
			window_flag_list.append(emmc_info_block[i].split()[-1])
			if '--' in emmc_info_block[i]:
				line_list = emmc_info_block[i].split()
				s_index = line_list.index('--')
				begin = int(line_list[s_index - 1], 16)
				end = int(line_list[s_index + 1], 16)
				window_width = end - begin + 1
				window_width_list.append(window_width)
				window_string = line_list[s_index - 1] + line_list[s_index] + line_list[s_index+1]
				window_string_list.append(window_string)
			else:
				line_list = emmc_info_block[i].split()
				window_width_list.append(width)
				window_string_list.append(line_list[-4])
	return temp, window_width_list, window_string_list, window_flag_list

def parse_emmc_arrange(emmc_info_block, emmc_info_list):
	temperature, width_l, string_l, flag_l = scrub_window_arrange(emmc_info_block)
	emmc_info_list.append(width_l)
	emmc_info_list.append(string_l)
	emmc_info_list.append(flag_l)
	emmc_info_dict = {temperature: emmc_info_list}
	return  emmc_info_dict

def get_nok_size(per_str_info):
	if '--' in per_str_info:
		line_list = per_str_info.split()
		separator_index = line_list.index('--')
		begin = int(line_list[separator_index - 1], 16)
		end = int(line_list[separator_index + 1], 16)
		nok_size = end - begin + 1
		return nok_size
	elif '-' in per_str_info:
		return 1

def list_all_files(rootdir):
	_files = []
	if os.path.isfile(rootdir):
		_files.append(rootdir)
		return _files
	list = os.listdir(rootdir)
	list.sort()
	for i in range(0, len(list)):
		file_path = os.path.join(rootdir, list[i])
		if os.path.isdir(file_path):
			_files.extend(list_all_files(file_path))
		if os.path.isfile(file_path):
			_files.append(file_path)
	return _files

def parse_emmc_block_info(per_str_info_list):
	per_win_info_list = []
	max_nok_size = 0
	win_range_list = []
	win_flag_list = []
	pattern = re.compile(r'\d+')
	if len(per_str_info_list) == 0:
		print('err: per info str list not exist')
		return per_str_info_list
	for i in range(0, len(per_str_info_list)):
		if 'current temperature is' in per_str_info_list[i]:
			temp = int(per_str_info_list[i].split()[-1], 10)
		elif 'best_start' in per_str_info_list[i]:
			line_list = per_str_info_list[i].split()
			index =	line_list.index('best_start')
			best_start = int(line_list[index + 1].strip(','), 16)
			best_size = int(line_list[index + 3].strip(','), 10)
			cmd_delay = int(line_list[-1], 16)
		elif 'cmd delay' in per_str_info_list[i] and 'nok' in per_str_info_list[i]:
			nok_size = get_nok_size(per_str_info_list[i])
		elif 'scan time' in per_str_info_list[i]:
			line_list = per_str_info_list[i].split()
			scan_time = int(line_list[-2], 10) / 1000000.0
		elif 'ds_sht' in per_str_info_list[i]:
			line_list = per_str_info_list[i].split()
			ds_sht = int(pattern.findall(line_list[3])[0], 10)
			window = int(pattern.findall(line_list[4])[0], 10)
	per_win_info_list.append(temp)
	per_win_info_list.append(best_start)
	per_win_info_list.append(best_size)
	per_win_info_list.append(cmd_delay)
	per_win_info_list.append(nok_size)
	per_win_info_list.append(scan_time)
	per_win_info_list.append(ds_sht)
	per_win_info_list.append(window)
	return per_win_info_list

def gene_info_block(lines):
	start = 0
	valid = 0
	search_start = "current temperature is"
	scan_end = 'emmc: new HS400 MMC'
	per_info_str_list = []
	for line in lines:
		if search_start in line:
			start = 1
		elif scan_end in line:
			start = 0
		if start == 1 and "meson-mmc" in line:
			per_info_str_list.append(line)
			if 'cmd delay' in line:
				valid = 1;
		if start == 0 and valid == 1 and len(per_info_str_list) > 0:
			valid = 0
			yield per_info_str_list
			per_info_str_list = []

def main():
	rootdir = sys.argv[1]
	file_list = list_all_files(rootdir)

	with open('reboot3.csv', 'w') as f:
		writer = csv.writer(f)
		writer.writerow(header)
		for file in file_list:
			with open(file, 'r') as log_file:
				lines = log_file.readlines()
				window_dict = {}
				for emmc_info in gene_info_block(lines):
					window_info_list = parse_emmc_block_info(emmc_info)
					window_info_dict = parse_emmc_arrange(emmc_info, window_info_list)
					window_dict.update(window_info_dict)
				print(sorted(window_dict.keys()))
				for d in sorted(window_dict):
					window_dict[d].insert(0, file)
					window_dict[d].insert(0, ' ')
					writer.writerow(window_dict[d])
if __name__ == '__main__':
	main()
