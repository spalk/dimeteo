# -*- coding: utf-8 -*-

from tkinter import *
import datetime as dt
import itertools

import db#, sensors

# Display resolution
X = 320	
Y = 240

class mgraf:
	"""Multi Graph Interface"""
		
	X0 = X/2
	Y0 = 10

	def __init__(self, canvas, default_color):
		self.canvas = canvas
		self.default_color = default_color
		self.bgnd_color = 'gray90'


		self.update_x_params()


	def update_x_params(self):
		
		## X-axis list
		
		# list of datetimes from the past to the future
		# - each 3 hours
		# - each 1 hour
		# - each 20 mins
		x_axis_list_3h = []
		x_axis_list_1h = []
		x_axis_list_20m = []

		# deepness to the past and to the future in hours
		depth = 27
			
		t_now = dt.datetime.now()
		self.t_now = t_now
		t_delta = dt.timedelta(hours = depth)
		t_from = t_now - t_delta
		self.t_from = t_from
		t_to = t_now + t_delta
		self.t_to = t_to
		
		t = t_from
		while t < t_to:
			t_round = t.replace(minute = 0, second = 0, microsecond = 0)
			
			# 1h
			x_axis_list_1h.append(t_round)

			# 3h
			if t.hour % 3 == 0:
				x_axis_list_3h.append(t_round)

			# 20min
			x_axis_list_20m.append(t_round)
			x_axis_list_20m.append(t_round + dt.timedelta(minutes = 20))
			x_axis_list_20m.append(t_round + dt.timedelta(minutes = 40))

			t += dt.timedelta(hours = 1)
			
		self.x_axis_list_3h = x_axis_list_3h
		self.x_axis_list_1h = x_axis_list_1h
		self.x_axis_list_20m = x_axis_list_20m
			
		
		## Density

		# Number of pixels in 20 min = 2px for width 320px
		self.density_20m = int(X / ((len(x_axis_list_1h) - 2) * 3 ))

		# Number of pixels in 1 hour
		self.density_1h = self.density_20m * 3

		# Number of pixels in 3 hour		
		self.density_3h = self.density_1h * 3

	
		## X-axis Shift
		#                          X0
		#                          |
		#  0      3      6      9  |    12      15      18      21
		#                    -->|  |<--
		#                        10:22
		#
		
		shift_delta = t_now - x_axis_list_3h[8]
		shift_delta_min = shift_delta.seconds / 60 # shift in minutes
		steps = int(shift_delta_min / 20) - 9
		self.x_axis_shift = steps * self.density_20m
		
		# X-axis coordinates
		x_center = X / 2
		x_start = x_center - depth * self.density_1h - self.x_axis_shift
		
		# 3h		
		x_axis_coords_3h = []
		coords = x_start
		for i in self.x_axis_list_3h:
			x_axis_coords_3h.append(coords)
			coords += self.density_3h
		self.x_axis_coords_3h = x_axis_coords_3h
		
		# 1h
		x_axis_coords_1h = []
		coords = x_start
		for i in self.x_axis_list_1h:
			x_axis_coords_1h.append(coords)
			coords += self.density_1h
		self.x_axis_coords_1h = x_axis_coords_1h
		
		# 20min
		x_axis_coords_20m = []
		coords = x_start
		for i in self.x_axis_list_20m:
			x_axis_coords_20m.append(coords)
			coords += self.density_20m
		self.x_axis_coords_20m = x_axis_coords_20m

		# 10min
		x_axis_coords_10m = []
		coords = x_start
		for i in self.x_axis_list_20m:
			x_axis_coords_10m.append(coords)
			coords += self.density_20m / 2
			x_axis_coords_10m.append(coords)
			coords += self.density_20m / 2
		self.x_axis_coords_10m = x_axis_coords_10m

	def x_axis(self, padding_bottom = 0, color = 0, angle = 0, font = 0):
		x_3h = self.x_axis_coords_3h
		x_1h = self.x_axis_coords_1h
		#x_20m = self.x_axis_coords_20m
		#x_10m = self.x_axis_coords_10m
		
		y = Y - padding_bottom
		labels = self.x_axis_list_3h
		
		if color == 0:
			color = self.default_color
		
		if font == 0:
			font = ('tahoma', 8)

	
		for i in range(len(labels)):
			self.canvas.create_text(
				x_3h[i],	
				y,
				text = labels[i].replace(minute = 0, second = 0).strftime('%H:%M'),
				fill = color,
				font = font,
				angle = angle,
				tags = 'x_labels'
			)
			if labels[i].hour == 0:
				self.canvas.create_line(
					x_3h[i],
					y-200,
					x_3h[i],
					y-14,
					fill = 'blue',
					dash=1,
					tags = 'x_dashes'
				)
				
		for i in range(len(x_1h)):
			self.canvas.create_line(
				x_1h[i],
				y-18,
				x_1h[i],
				y-14,
				tags = 'x_dashes'
			)
				
	def center_line (self, y_from, y_to, color):
		self.canvas.create_line(X/2, y_from, X/2, y_to, fill = color, width = 2)
		
	def update_y_params(self, y_from, y_to):
		self.y_from = y_from
		self.y_to = y_to
		
		db_data =  db.Gui_Data()
		
		# Max|Min values of temperature in diapson from -depth to +depth
		max_temp = db_data.get_max_temp(self.t_from, self.t_now)
		min_temp = db_data.get_min_temp(self.t_from, self.t_now)
		max_forc = db_data.get_max_forecast(self.t_from, self.t_to)
		min_forc = db_data.get_min_forecast(self.t_from, self.t_to)
		y_max = max(max_temp, max_forc)
		y_min = min(min_temp, min_forc)
		
		# Function which returns temp value in pix, depends on Min|Max
		def y_graf (val, val_min, val_max, y_graph_from, y_graph_to):
			H_pix = y_graph_to - y_graph_from
			H_grad = val_max - val_min
			one_grad_in_pix = int(H_pix / H_grad)
			t_delta = (val - val_min) * one_grad_in_pix
			t_y = y_graph_to - t_delta
			return int(t_y)
		
		
		## History graph Y and XY coordinates calculating
		
		# dict for labels:
		# x, y, val, name
		temp_labels = []

		# DS18B20 sensor each 20 minutes average temperatur calculating
		vals = []
		count = 0
		temp_labels_indexes = []
		for i in self.x_axis_list_20m:
			if i < self.t_now:
				t_avg = db_data.get_sensor_avg(
						i - dt.timedelta(minutes = 20),
						i,
						'temp_DS18B20'
					)[0][0]
				vals.append(round(t_avg, 2))

				if i.minute == 0 and i.hour in (0,3,6,9,12,15,18,21):
					temp_labels.append({
						'name':'history',
						'value':int(t_avg)
						})
					temp_labels_indexes.append(count)
				count += 1
		self.temp_history_vals_20m = vals
		
		# Y coords for temp history (from -depth till now)
		y_history_coords = []
		for t in vals:
			y_c = y_graf(t, y_min, y_max, self.y_from, self.y_to)
			y_history_coords.append(y_c)
		
		# XY coords for temp history
		history_temp_coords = []
		count = 0
		for i in range(len(y_history_coords)):
			x = self.x_axis_coords_20m[i] + self.x_axis_shift
			history_temp_coords.append(
					(
					x,
					y_history_coords[i]
					)
				)
			if i in temp_labels_indexes:
				temp_labels[count]['x'] = x
				temp_labels[count]['y'] = y_history_coords[i]
				count += 1

		self.history_temp_coords = history_temp_coords
		
		
		# RP5.ru
		rp_vals = db_data.get_forecats_data(self.t_now, self.t_to, 'rp5.ru')
		
		frc_rpf_temp_coords = []
		frc_rpf_temp_coords.append(history_temp_coords[len(history_temp_coords)-1])
		for i in range(len(self.x_axis_list_3h)):
			if self.x_axis_list_3h[i] > self.t_now:
				for n in rp_vals:
					rp_dt = dt.datetime.strptime(n[2], '%Y-%m-%d %H:%M:%S')
					if self.x_axis_list_3h[i].hour == rp_dt.hour and \
					   self.x_axis_list_3h[i].day == rp_dt.day:
						x = self.x_axis_coords_3h[i] + self.x_axis_shift
						y = y_graf(n[3], y_min, y_max, self.y_from, self.y_to)
						frc_rpf_temp_coords.append(
								(
								x,
								y
								)
							)
						temp_labels.append({
							'x':x,
							'y':y,
							'value':int(n[3]),
							'name':'rp5'
						})
		self.frc_rpf_temp_coords = frc_rpf_temp_coords

		# OpenWeatherMap.org
		owm_vals = db_data.get_forecats_data(self.t_now, self.t_to, 'OpenWeatherMap.org')
		
		frc_owm_temp_coords = []
		frc_owm_temp_coords.append(history_temp_coords[len(history_temp_coords)-1])
		for i in range(len(self.x_axis_list_3h)):
			if self.x_axis_list_3h[i] > self.t_now:
				for n in owm_vals:
					owm_dt = dt.datetime.strptime(n[2], '%Y-%m-%d %H:%M:%S')
					if self.x_axis_list_3h[i].hour == owm_dt.hour and \
					   self.x_axis_list_3h[i].day == owm_dt.day:
						x = self.x_axis_coords_3h[i]+self.x_axis_shift
						y = y_graf(n[3], y_min, y_max, self.y_from, self.y_to)
						frc_owm_temp_coords.append(
							(
								x,
								y
							)
						)
						temp_labels.append({
							'x':x,
							'y':y,
							'value':int(n[3]),
							'name':'owm'
						})
		self.frc_owm_temp_coords = frc_owm_temp_coords

		self.temp_labels = temp_labels
		
		
		# Horozontal lines
		self.y_horizontals_temp = list(range(int(y_min), int(y_max)+1))
		self.y_horizontals_coords = []
		for t in self.y_horizontals_temp:
			self.y_horizontals_coords.append(y_graf(t, y_min, y_max, self.y_from, self.y_to))
		


		## Vertical lines
		for i in temp_labels:
			try:
				self.canvas.create_line(
					i['x'],
					i['y'], # vertical shift from graf
					i['x'],
					200, # distance to x-axis,
					dash = 4,
					fill = 'medium orchid'
				)
			except:
				pass

	def graf(self):

		# Graph History
		graf_line = self.canvas.create_line(
			self.history_temp_coords,
			fill = 'green2',
			smooth = 1,
			width = 3,
			tags = 'graph_hist'
		)

		# Graph Forecast RP5
		graf_forecast_rpf_line = self.canvas.create_line(
			self.frc_rpf_temp_coords,
			fill = 'blue2',
			smooth = 0,
			#splinesteps = 1,
			width = 2,
			tags = 'graph_forecast_rp5'
		)
		
		# Graph Forecast OpenWeatherMap
		graf_forecast_owm_line = self.canvas.create_line(
			self.frc_owm_temp_coords,
			fill = 'orange2',
			#smooth = 0,
			width = 2,
			tags = 'graph_forecast_owm'
		)
	
	def horizontals(self):
		y_coords = self.y_horizontals_coords
		y_temps = self.y_horizontals_temp
		for i in range(len(y_coords)):
			self.canvas.create_line(
			0, y_coords[i], 320, y_coords[i],
			fill = 'gray80',
			tags = 'horizontal'
			)
			
	def horizontals_labels(self):
		y_coords = self.y_horizontals_coords
		y_temps = self.y_horizontals_temp
		for i in range(len(y_coords)):
			y = y_coords[i]
			for x in (8, 310):
				self.canvas.create_rectangle(
					x-8, y-3, x+8, y+3,
					fill = self.bgnd_color,
					width=0
					)		

				self.canvas.create_text(
					x, y,
					text = y_temps[i],
					fill = 'gray50',
					font = ('tahoma', 6),
					tags = 'horiz_labels'
					)

	def temper_labels(self):
		# Color Scheme should be Global. Replace somewhere to the top [TODO]
		self.color_scheme = {
				'history':'green',
				'rp5':'blue',
				'owm':'orange4'
				}

		shift = (0,-10) # for all labels
		y_shift = 10 # for multiple labels

		def get_another_y(x, cur_name):
			result = False
			
			if cur_name == 'rp5':
				f_name = 'owm'
			else:
				f_name = 'rp5'
						
			for p in self.temp_labels:
				if p['x'] == x and p['name'] == f_name:
					result = p['y']
			return result
			
		for point in self.temp_labels:
			try:
				if point['name'] == 'history':
					x = point['x'] + shift[0]
					y = point['y'] + shift [1]

				else:
					another_y = get_another_y(point['x'], point['name'])
					if another_y:
						print(another_y)
						if point['y'] < another_y:
							x = point['x'] + shift[0]
							y = point['y'] + shift[1] - shift_y
						else:
							x = point['x'] + shift[0]
							y = another_y + shift[1]

					else:
						x = point['x'] + shift[0]
						y = point['y'] + shift[1]
			except:
				pass
			self.canvas.create_text(
				x,
				y,
				text = point['value'],
				fill = self.color_scheme[point['name']],
				font = ('tahoma',6)
			)
	



class Interface(Tk):
	def __init__(self, *args, **kwargs):
		Tk.__init__(self, *args, **kwargs)

		window = Toplevel(self,  bg='gray90')
		window.overrideredirect(1)
		window.geometry('%sx%s' % (X, Y))
		
		self.canvas = Canvas(window, width = X, height= Y)

		self.intf = mgraf(self.canvas, 'gray90')
		self.intf.x_axis(15, 'green', 90, ('tahoma', 7))
		self.intf.center_line(0, 204, 'red')
		self.intf.update_y_params(60, 200)
		self.intf.horizontals()
		self.intf.graf()
		#self.intf.horizontals_labels()
		self.intf.temper_labels()
		
	
		self.canvas.pack()
		
		self.update_x_axis()
		
		
	
	def update_x_axis(self):
		self.intf.update_x_params()
		self.canvas.delete("x_dashes", "x_labels")
		self.intf.x_axis(15, 'green', 90, ('tahoma', 7))
		self.after(5000, self.update_x_axis) # 5 min
		
		
	

root = Interface()
root.mainloop()





## Offset from phisical display border
#global_padding = (3, 3, 3, 3) # pix

## Background color
#global_bgnd_color = 'white'

#class graf:
    #def __init__(self, canvas, position_from, position_to, color = 'blue', border = 0, border_color = 0): #position in %
        #self.canvas = canvas
        ## position from to in pixels
        #self.position_from = (int(position_from[0] * X), int(position_from[1] * Y))
        #self.position_to = (int(position_to[0] * X), int(position_to[1] * Y))
        #self.color = color
        #self.W = self.position_from[0] - self.position_to[0]
        #self.H = self.position_from[1] - self.position_to[1]
        #if border_color == 0:
            #border_color = self.color
        #if border == 1:
            #self.canvas.create_rectangle(self.position_from, self.position_to, outline = border_color)

    #def add_title(self, text, position = (0,0), font = ('tahoma', 8), color = 0, tag = ''):
        #if color == 0:
            #color = self.color
        #self.title_text = text
        #self.title_position = (self.position_from[0] + position[0], self.position_from[1] + position[1])
        #self.tit = self.canvas.create_text(self.title_position[0], self.title_position[1], text = self.title_text, fill=color, font=font, tags = tag)

    #def add_graf(self, graf_padding, data, smooth = 0, border = 0, border_color = 0, tag = ''):
        #self.data = data
        #self.graf_point_start = (self.position_from[0] + graf_padding[3], self.position_from[1] + graf_padding[0])
        #self.graf_point_end = (self.position_to[0] - graf_padding[1], self.position_to[1] - graf_padding[2])
        #self.graf_H = self.graf_point_end[1] - self.graf_point_start[1]
        #self.graf_W = self.graf_point_end[0] - self.graf_point_start[0]
        #self.step_x = self.graf_W / len(data)
        #self.step_y = (max(self.data.values()) - min(self.data.values())) / self.graf_H  # value in 1 pix
        #self.graf_line = self.canvas.create_line(self.graf_data_prepar(self.data.values()), smooth=smooth, fill = self.color, tags = tag)
        #if border_color == 0:
            #border_color = self.color
        #if border == 1:
            #self.canvas.create_rectangle(self.graf_point_start, self.graf_point_end, outline = border_color)

    #def step_y_update(self, data):
        #self.step_y = (max(data.values()) - min(data.values())) / self.graf_H  # value in 1 pix

    #def graf_data_prepar(self, d):
        #graf_x = self.graf_point_start[0]
        #data_ready = []
        #for i in d:
            #n = []
            #n.append(int(graf_x))
            #n.append(self.graf_point_end[1] - int((i - min(d)) / self.step_y))
            #graf_x += self.step_x
            #data_ready.append(n)
        #return data_ready


    #def add_x_axe(self, dash_length = 5, dash_shift = 4, x_dash_color = 0, x_lable_color = 0, x_lables_shift = (0,0), x_labels_font=('tahoma', 6), lables_number_limit = 24, x_lable_angle = 90):
        #x_axe_lables_list = list(self.data.keys())
        #x_dash_x = self.graf_point_start[0]
        #y_dash_y = self.position_to[1]
        #lable_filter = int(len(self.data) / lables_number_limit)
        #if x_lable_color == 0:
            #x_lable_color = self.color
        #if x_dash_color == 0:
            #x_dash_color = self.color
        #count = 0
        #for i in x_axe_lables_list:
            #self.canvas.create_line(x_dash_x, y_dash_y + dash_shift, x_dash_x, y_dash_y + dash_shift - dash_length, fill = x_dash_color, tags = 'x_dashes')
            #if count % lable_filter == 0:
                #self.canvas.create_text(x_dash_x + x_lables_shift[0], y_dash_y + x_lables_shift[1], text = i, fill = x_lable_color, font = x_labels_font, angle = x_lable_angle, tags = 'x_labels')
            #count += 1
            #x_dash_x += self.step_x

    #def add_y_axe(self, dash_length = 5, dash_shift = 4, y_dash_color = 0, y_lable_color = 0, y_lables_shift = (0,0), y_labels_font=('tahoma', 6)):
        #min_y = min(self.data.values())
        #max_y = max(self.data.values())
        #y_axe_lables_list = list(range(int(min_y), int(max_y)+1))
        #y_axe_lables_list.pop(0)
        #x_dash_x = self.graf_point_start[0]
        #y_dash_y = self.graf_point_end[1]
        #if y_lable_color == 0:
            #y_lable_color = self.color
        #if y_dash_color == 0:
            #y_dash_color = self.color
        #for i in y_axe_lables_list:
            #xf = x_dash_x + dash_shift
            #yf = y_dash_y - int((i - min_y) / self.step_y)
            #xt = x_dash_x + dash_shift + dash_length
            #yt = y_dash_y - int((i - min_y) / self.step_y)
            #self.canvas.create_line(xf, yf, xt, yt, fill = y_dash_color, tags = 'y_dashes')
            #self.canvas.create_text(x_dash_x + y_lables_shift[0], yf + y_lables_shift[1], text = i, fill = y_lable_color, font = y_labels_font, tags = 'y_labels')
            #y_dash_y += self.step_y
        #print ('ups')



#class Interface(Tk):
    #def __init__(self, *args, **kwargs):
        #Tk.__init__(self, *args, **kwargs)

        ## get data
        #d = db.Gui_Data().get_temp_24h()

        #t3 = Toplevel(self,  bg='gray')
        #t3.overrideredirect(1)
        #t3.geometry('%sx%s' % (X, Y)) # сделать определение разрешения экрана

        #self.canvas = Canvas(t3, width = X, height= Y)

        #curtime = datetime.datetime.now().strftime('%H:%M:%S')
        #self.sensors = sensors.sensors()
        #curtemp_out = 'Temp Out: %s' % round(self.sensors.read_temp_DS18B20(), 2)
        #curtemp_in = 'Temp In: %s' % round(self.sensors.read_temp_BME280(), 2)

        #self.temp = graf(self.canvas, (0,0), (1,1), border = 1, border_color = 'red')
        #self.temp.add_graf((20,5,28,25), d, smooth = 1, border = 1, tag = 'graf_temp_out')
        #self.temp.add_x_axe(4, dash_shift = -24, x_lables_shift=(0, -11), x_lable_color = 'dark slate gray', x_lable_angle = 90)
        #self.temp.add_y_axe(300, dash_shift = -4, y_dash_color = 'SteelBlue2',  y_lables_shift=(-10, 0), y_labels_font=('tahoma', 8))
        #self.temp.add_title(curtime, position = (50,10), font = ('tahoma', 9), color = 'green', tag = 'time')
        #self.temp.add_title(curtemp_out, position = (265,10), font = ('tahoma', 9), color = 'red', tag = 'cur_temp_out')
        #self.temp.add_title(curtemp_in, position = (150,10), font = ('tahoma', 9), color = 'purple', tag = 'cur_temp_in')
        #self.canvas.pack()


        #self.update_clock()
        #self.update_graf()
        #self.update_axes()
        #self.update_cur_temp()

    #def update_clock(self):
        #curtime = datetime.datetime.now().strftime("%H:%M:%S")
        #self.canvas.itemconfig("time", text = curtime)
        ## call this function again in one second
        #self.after(1000, self.update_clock)

    #def update_cur_temp(self):
        #curtemp_out = 'Temp Out: %s' % round(self.sensors.read_temp_DS18B20(), 2)
        #curtemp_in = 'Temp In: %s' % round(self.sensors.read_temp_BME280(), 2)
        #self.canvas.itemconfig("cur_temp_out", text = curtemp_out)
        #self.canvas.itemconfig("cur_temp_in", text = curtemp_in)
        #self.after(5000, self.update_cur_temp)

    #def update_graf(self):
        #fresh_data = db.Gui_Data().get_temp_24h()
        #self.temp.step_y_update(fresh_data)
        #prepar_data = self.temp.graf_data_prepar(list(fresh_data.values()))
        #self.canvas.coords('graf_temp_out', *flatten(prepar_data))
        #self.after(10000, self.update_graf)

    #def update_axes(self):
        #fresh_data = db.Gui_Data().get_temp_24h()
        #self.temp.data = fresh_data
        #self.canvas.delete("x_dashes", "y_dashes", "x_labels", "y_labels")
        #self.temp.add_x_axe(4, dash_shift = -24, x_lables_shift=(0, -11), x_lable_color = 'dark slate gray', x_lable_angle = 90)
        #self.temp.add_y_axe(300, dash_shift = -4, y_dash_color = 'SteelBlue2',  y_lables_shift=(-10, 0), y_labels_font=('tahoma', 8))

        #self.after(30000, self.update_axes)



## from itertools recipes: https://docs.python.org/2/library/itertools.html
#def flatten(list_of_lists):
    #"""Flatten one level of nesting"""
    #return itertools.chain.from_iterable(list_of_lists)











##temp.title_text = 'Temperature, C ' + datetime.datetime.now().strftime('%H:%M:%S')







##### Color scheme

###day
###night


#### Global
###background

#### Graf
###background
###title
###x_axe_dash
###x_axe_lables
###y_axe_dash
###y_axe_lables = graf


##canvas.pack()

##root.mainloop()

##
