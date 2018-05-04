#!/usr/bin/env python3

"""per2csv.py: converts PET's log files (.per) to csv

call as: python3 per2csv.py [an arbitrary number of per files]

Author: Antonio Toral
License: GPL v3
"""


import sys
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

# own functions
from per2csv_functions import time2seconds, check_annotation_done



#prints the header for the csv file
def print_header():
	print("id", "subject", "item", "tasktype", "translation_type", "len_sl_chr", "len_tl_chr", "len_sl_wrd", "len_tl_wrd", "edit_time", "k_total", "k_letter", "k_digit", "k_white", "k_symbol", "k_nav", "k_erase", "k_copy", "k_cut", "k_paste", "k_do", "np_300", "lp_300", "np_1000", "lp_1000", "ev_time", "num_annotations", sep = '\t')



def parse_per_file(finput):
	tree = ET.ElementTree(file=finput)
	check_annotation_done(tree)
	j_id = tree.getroot().get('id')
	#print(tree.getroot().attrib)

	for e_unit in tree.iterfind('unit'):
		subject = ""
		item = ""
		tasktype = ""
		s_len_sl_chr = 0
		s_len_tl_chr = 0
		s_len_sl_wrd = 0
		s_len_tl_wrd = 0
		edit_time = 0
		k_letter = 0
		k_digit = 0
		k_white = 0
		k_symbol = 0
		k_nav = 0
		k_erase = 0
		k_copy = 0
		k_cut = 0
		k_paste = 0
		k_do = 0
		k_total = 0

		# pauses
		t_cur = 0
		t_prev = 0
		np_300 = 0 # num pauses >= 300ms
		lp_300 = 0 # time pauses >= 300ms
		np_1000 = 0 # num pauses >= 1000ms
		lp_1000 = 0 # time pauses >= 1000ms
		n_event = 0
		event_time = 0 # time (ms) extracted from elements children of events. It should be the same of edit_time (extracted from <indicator id="editing" type="time">)
		num_annotations = 0


		#print(e_unit.tag, e_unit.attrib)

		u_id = e_unit.get('id')

		for e_sl in e_unit.iterfind('S'):
			s_len_sl_chr = len(e_sl.text)
			s_len_sl_wrd = len(e_sl.text.split())



		for e_ann in e_unit.iterfind('annotations/annotation'):
			#print (e_ann.tag, e_ann.attrib)


			if e_unit.get('type') == 'pe':
				for e_tl in e_ann.iterfind('PE'):
					#print("PE ", len(e_tl.text))
					s_len_tl_chr = len(e_tl.text)
					s_len_tl_wrd = len(e_tl.text.split())
					subject = e_tl.get('producer').split(".")[0]
			else: #if e_unit.get('type') == 'ht':
				for e_tl in e_ann.iterfind('HT'):
					s_len_tl_chr = len(e_tl.text)
					s_len_tl_wrd = len(e_tl.text.split())
					subject = e_tl.get('producer')


			for e_time in e_ann.findall("indicator[@id='editing']"): #[@type='time']"):
				#print(e_time.text)
				#print(time2seconds(e_time.text))
				edit_time += time2seconds(e_time.text)


			for e_kl in e_ann.findall("indicator[@id='letter-keys']"):
				k_letter += int(e_kl.text)
			for e_kd in e_ann.findall("indicator[@id='digit-keys']"):
				k_digit += int(e_kd.text)
			for e_kw in e_ann.findall("indicator[@id='white-keys']"):
				k_white += int(e_kw.text)
			for e_ks in e_ann.findall("indicator[@id='symbol-keys']"):
				k_symbol += int(e_ks.text)
			for e_kn in e_ann.findall("indicator[@id='navigation-keys']"):
				k_nav += int(e_kn.text)
			for e_ke in e_ann.findall("indicator[@id='erase-keys']"):
				k_erase += int(e_ke.text)
			for e_kc in e_ann.findall("indicator[@id='copy-keys']"):
				k_copy += int(e_kc.text)
			for e_kcu in e_ann.findall("indicator[@id='cut-keys']"):
				k_cut += int(e_kcu.text)
			for e_kp in e_ann.findall("indicator[@id='paste-keys']"):
				k_paste += int(e_kp.text)
			for e_kdo in e_ann.findall("indicator[@id='do-keys']"):
				k_do += int(e_kdo.text)



			# pauses
			event_time_annotation = 0
			for e_event in e_ann.iterfind('events'):
				n_event +=1
				#print("EVENT ", n_event)
				for e_event_child in e_event.getchildren():
					event_time_annotation = int(e_event_child.get("t")) #this is overwriten for each chile, so it will be recorded for the last child, thus giving the editing time

					if(e_event_child.tag != "keystroke" and e_event_child.tag != "command"): #we only consider pauses between elements keystroke and command
						continue

					t_cur = int(e_event_child.get("t"))
					#print(t_cur, t_prev)

					if t_cur - t_prev >= 300:
						np_300 += 1
						lp_300 += t_cur - t_prev
						#print(">= 300", np_300, lp_300)

						if t_cur - t_prev >= 1000:
							np_1000 += 1
							lp_1000 += t_cur - t_prev
							#print(">= 1000", np_1000, lp_1000)

					t_prev = t_cur

			event_time += event_time_annotation
			num_annotations += 1



		k_total += k_letter + k_digit + k_white + k_symbol + k_nav + k_erase + k_copy + k_cut + k_paste + k_do
		item = j_id.rsplit("-", 1)[0] + u_id
		tasktype = j_id.rsplit("-", 1)[1]


		print(j_id+ "-" + u_id, subject, item, tasktype, e_unit.get('type'), s_len_sl_chr, s_len_tl_chr, s_len_sl_wrd, s_len_tl_wrd, edit_time, k_total, k_letter, k_digit, k_white, k_symbol, k_nav, k_erase, k_copy, k_cut, k_paste, k_do, np_300, lp_300, np_1000, lp_1000, event_time, num_annotations, sep = '\t')


		# debug edit_time vs event_time
		#print(float(edit_time)*1000, float(event_time)*0.99, event_time, file=sys.stderr)
		edit_time_ms = float(edit_time)*1000
		if (edit_time_ms < float(event_time)*0.995 or edit_time_ms > float(event_time)*1.005):
			rel_diff = (float(event_time) - edit_time_ms) / edit_time_ms
			print(j_id+"-"+u_id, edit_time_ms, float(event_time), rel_diff, num_annotations, file=sys.stderr)
		#sys.exit(0)




print_header()
for i in sys.argv[1:]:
	parse_per_file(i)








