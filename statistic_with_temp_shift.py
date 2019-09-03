import os
import time
import sys
import csv
import math

header = ['vendor', 'file_path', 'temperature', 'repeat times',
		'command window start mean', 'command window start std',
		'command window size mean', 'command window size std',
		'min command window size', 'command delay mean',
		'max nok size mean', 'max nok size std', 'min nok size',
		'scan time mean', 'scan time std', 'max scan time',
		'window arrange', 'window width', 'window flag']

def compute_distribution(list):
	if len(list) == 0:
		return 0, 0
	sum1 = 0
	average = round(float(sum(list)/len(list)),2)
	for value in list:
		sum1 += (value - average) ** 2
		stddev = round(math.sqrt(sum1/len(list)),2)
	return average, stddev

def check_info_list(per_win_info_list):
	for i in range(0, len(per_win_info_list)):
		if per_win_info_list[i].isdigit:
			return 0
	return 1

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

def seperate_by_temperature(all_info_list):
	classf_by_temp_list = []
	temp_0_list = []
	temp_5_list = []
	temp_15_list = []
	temp_25_list = []
	temp_35_list = []
	temp_45_list = []
	temp_55_list = []
	temp_65_list = []
	temp_70_list = []
	for i in range(0, len(all_info_list)):
		temp0 = all_info_list[i][0]
		temp1 = all_info_list[i][1]
		if temp0 - temp1 > 5000:
			print(temp0, temp1)
			continue
		if temp0 < 0:
			temp_0_list.append(all_info_list[i])
		elif  temp0 > 0 and temp0 < 10000:
			temp_5_list.append(all_info_list[i])
		elif  temp0 > 10000 and temp0 < 20000:
			temp_15_list.append(all_info_list[i])
		elif  temp0 > 20000 and temp0 < 30000:
			temp_25_list.append(all_info_list[i])
		elif  temp0 > 30000 and temp0 < 40000:
			temp_35_list.append(all_info_list[i])
		elif  temp0 > 40000 and temp0 < 50000:
			temp_45_list.append(all_info_list[i])
		elif  temp0 > 50000 and temp0 < 60000:
			temp_55_list.append(all_info_list[i])
		elif  temp0 > 60000 and temp0 < 70000:
			temp_65_list.append(all_info_list[i])
		else :
			temp_70_list.append(all_info_list[i])
	classf_by_temp_list.append(temp_0_list)
	classf_by_temp_list.append(temp_5_list)
	classf_by_temp_list.append(temp_15_list)
	classf_by_temp_list.append(temp_25_list)
	classf_by_temp_list.append(temp_35_list)
	classf_by_temp_list.append(temp_45_list)
	classf_by_temp_list.append(temp_55_list)
	classf_by_temp_list.append(temp_65_list)
	classf_by_temp_list.append(temp_70_list)
	return classf_by_temp_list

def statistic_win_info(classf_by_temp_list, width_dict, arrange_dict, flag_dict):
	statistic_win_info_list = []
	statistic_per_temp_info_list = []
	min_best_size = 0
	min_nok_size = 0
	repeat_times = 0
	max_scan_time = 0
	temp_list = [-5,5,15,25,35,45,55,65,75]

	for i in range(0, len(classf_by_temp_list)):
		statistic_per_temp_info_list = []
		best_start_list = []
		best_size_list = []
		cmd_delay_list = []
		max_nok_size_list = []
		scan_time_list = []
		key = temp_list[i]
		for j in range(0, len(classf_by_temp_list[i])):
			best_start_list.append(classf_by_temp_list[i][j][2])
			best_size_list.append(classf_by_temp_list[i][j][3])
			cmd_delay_list.append(classf_by_temp_list[i][j][4])
			max_nok_size_list.append(classf_by_temp_list[i][j][5]) 
			scan_time_list.append(classf_by_temp_list[i][j][6])
		repeat_times = len(best_start_list)
		if len(best_size_list) > 0:
			min_best_size = min(best_size_list)
		if len(max_nok_size_list) > 0:
			min_nok_size = min(max_nok_size_list)
		if len(scan_time_list) > 0:
			max_scan_time = max(scan_time_list)
		best_start_mean, best_start_std = compute_distribution(best_start_list)
		best_size_mean, best_size_std = compute_distribution(best_size_list)
		cmd_delay_mean, cmd_delay_std = compute_distribution(cmd_delay_list)
		max_nok_size_mean, max_nok_size_std = compute_distribution(max_nok_size_list)
		scan_time_mean, scan_time_std = compute_distribution(scan_time_list)
		statistic_per_temp_info_list.append(repeat_times)
		statistic_per_temp_info_list.append(best_start_mean)
		statistic_per_temp_info_list.append(best_start_std)
		statistic_per_temp_info_list.append(best_size_mean)
		statistic_per_temp_info_list.append(best_size_std)
		statistic_per_temp_info_list.append(min_best_size)
		statistic_per_temp_info_list.append(cmd_delay_mean)
		statistic_per_temp_info_list.append(max_nok_size_mean)
		statistic_per_temp_info_list.append(max_nok_size_std)
		statistic_per_temp_info_list.append(min_nok_size)
		statistic_per_temp_info_list.append(scan_time_mean)
		statistic_per_temp_info_list.append(scan_time_std)
		statistic_per_temp_info_list.append(max_scan_time)
		statistic_per_temp_info_list.append(arrange_dict[key])
		statistic_per_temp_info_list.append(width_dict[key])
		statistic_per_temp_info_list.append(flag_dict[key])
		statistic_win_info_list.append(statistic_per_temp_info_list)
	return statistic_win_info_list

def scrub_window_arrange(per_str_info_list, temp_list):
	window_width_list = []
	window_flag_list = []
	window_string_list = []
	width = 1
	try: 
		temp = int(per_str_info_list[-1], 10)
		index = temp_list.index(temp)
	except:
		return 0, 0, 0, 0

	for i in range(0, len(per_str_info_list)):
		if 'cmd delay' in per_str_info_list[i]:
			window_flag_list.append(per_str_info_list[i].split()[-1])
			if '--' in per_str_info_list[i]:
				line_list = per_str_info_list[i].split()
				s_index = line_list.index('--')
				begin = int(line_list[s_index - 1], 16)
				end = int(line_list[s_index + 1], 16)
				window_width = end - begin + 1
				window_width_list.append(window_width)
				window_string = line_list[s_index - 1] + line_list[s_index] + line_list[s_index+1]
				window_string_list.append(window_string)
			else:
				line_list = per_str_info_list[i].split()
				window_width_list.append(width)
				window_string_list.append(line_list[-4])
	return index, window_width_list, window_string_list, window_flag_list

def scrub_window_arrange_list(lines, temp_list):
	start = 0
	#scan_end = 'Emmc scan command window'
	#temp = 'temp0'
	temp = "scan time distance"
	scan_end = "temp1"

	per_info_str_list = []
	width_l = [0, 0, 0, 0, 0, 0, 0, 0, 0]
	string_l = [0, 0, 0, 0, 0, 0, 0, 0, 0]
	flag_l = [0, 0, 0, 0, 0, 0, 0, 0, 0]
	for line in lines:
		per_info_win_list = []
		if temp in line:
			start = 1
		elif scan_end in line:
			start = 0
		if start == 1:
			per_info_str_list.append(line)
		if start == 0 and len(per_info_str_list) > 0:
			index, width_list, string_list, flag_list = scrub_window_arrange(per_info_str_list, temp_list)
			per_info_str_list = []
			if width_list == 0:
				continue
			width_l[index] = width_list
			string_l[index] = string_list
			flag_l[index] = flag_list
	return width_l, string_l, flag_l

def scrub_closest_temp_list(lines):
	find_temp = 0
	temp_list = [0, 0, 0, 0, 0, 0, 0, 0, 0]
	temp = 0
	for line in lines:
		if 'temp0' in line:
			find_temp = 1
		elif find_temp == 1:
			try:
				temp = int(line, 10)
			except:
				find_temp = 0
				continue
			find_temp = 0
			index = temp / 10000 + 1
			index = max(0, index)
			index = min(8, index)
			mid_temp = (10 * index - 5) * 1000
			if abs(temp_list[index] - mid_temp) > abs(temp - mid_temp):
				temp_list[index] = temp 
	return temp_list

def build_window_shift_result(lines):
	temp_key_list = [-5, 5, 15, 25, 35, 45, 55, 65, 75]
	temp_list = scrub_closest_temp_list(lines)
	width_l, string_l, flag_l = scrub_window_arrange_list(lines, temp_list)
	width_dict = dict(zip(temp_key_list, width_l))
	string_dict = dict(zip(temp_key_list, string_l))
	flag_dict = dict(zip(temp_key_list, flag_l))
	return width_dict, string_dict, flag_dict

def sparse_str_list(per_str_info_list):
	per_win_info_list = []
	max_nok_size = 0
	win_range_list = []
	win_flag_list = []
	if len(per_str_info_list) == 0:
		print('err: per info str list not exist')
		return per_str_info_list
	for i in range(0, len(per_str_info_list)):
		if 'temp0' in per_str_info_list[i]:
			temp0 = int(per_str_info_list[i+1], 10)
		#elif 'temp1' in per_str_info_list[i]:
			#temp1 = int(per_str_info_list[i+1], 10)
			temp1 = temp0
		elif 'best_start' in per_str_info_list[i]:
			line_list = per_str_info_list[i].split()
			index =	line_list.index('best_start')
			best_start = int(line_list[index + 1].strip(','), 16)
			best_size = int(line_list[index + 3].strip(','), 10)
			cmd_delay = int(line_list[-1], 16)
		elif 'cmd delay' in per_str_info_list[i] and 'nok' in per_str_info_list[i]:
			nok_size = get_nok_size(per_str_info_list[i])
			max_nok_size = max(nok_size, max_nok_size)
		elif 'scan time' in per_str_info_list[i]:
			line_list = per_str_info_list[i].split()
			scan_time = int(line_list[-2], 10) / 1000000.0
	per_win_info_list.append(temp0)
	per_win_info_list.append(temp1)
	per_win_info_list.append(best_start)
	per_win_info_list.append(best_size)
	per_win_info_list.append(cmd_delay)
	per_win_info_list.append(max_nok_size)
	per_win_info_list.append(scan_time)
	print(per_win_info_list)
	return per_win_info_list

def sparse_file(lines):
	start = 0
	temp = 'temp0'
	search_start = "scan time distance"
	scan_end = 'temp1'
	all_info_win_set_list = []
	per_info_str_list = []
	width_dict, arrange_dict, flag_dict= build_window_shift_result(lines)
	for line in lines:
		per_info_win_list = []
		if search_start in line:
			start = 1
		elif scan_end in line:
			start = 0
		if start == 1:
			per_info_str_list.append(line)
		if start == 0 and len(per_info_str_list) > 0:
			try:
				per_info_win_list = sparse_str_list(per_info_str_list)
			except:
				pass
			per_info_str_list = []
		if len(per_info_win_list) > 0:
			all_info_win_set_list.append(per_info_win_list)
	classf_by_temp_list = seperate_by_temperature(all_info_win_set_list)
	statis_win_info_list = statistic_win_info(classf_by_temp_list, width_dict, arrange_dict, flag_dict)
	return statis_win_info_list

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

def construct_row_info(statis_win_info_list):
	temp_str = ' '
	all_temp_list = []
	for i in range(0, len(statis_win_info_list)):
		row_list = []
		row_list.append(i*10-5)
		row_list.extend(statis_win_info_list[i])
		all_temp_list.append(row_list)
	return all_temp_list

def main():
	rootdir = sys.argv[1]
	file_list = list_all_files(rootdir)

	with open('sm1_hs400_200m_temp_shift_distribution_file.csv', 'w') as f:
		writer = csv.writer(f)
		writer.writerow(header)
		for file in file_list:
			print(file)
			head_info_per_row = []
			with open(file, 'r') as log_file:
				head_info_per_row.append(' ')
				head_info_per_row.append(file)
				lines = log_file.readlines()
				if 1:
					statis_win_info_list = sparse_file(lines)
					construct_row_list = construct_row_info(statis_win_info_list)
					for row_list in construct_row_list:
						statistic_info_per_row = []
						statistic_info_per_row.extend(head_info_per_row)
						statistic_info_per_row.extend(row_list)
						writer.writerow(statistic_info_per_row)
				#except:
				#	print('error: %s sparse failed' %(file))
				#	continue
if __name__ == '__main__':
	main()
